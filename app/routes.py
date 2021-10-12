from time import gmtime
from azure.storage import blob
from werkzeug.utils import redirect
from app import app, db
from flask import render_template, url_for, request, session, flash, redirect
from app.models import Users, Rentals
import msal
import copy
import os, uuid
from datetime import date, datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__, BlobPrefix, generate_container_sas, ContainerSasPermissions

import requests
from app import app_config

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

'''
Welcome page, logs user into DB if needed
'''
@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    else:
         # search for current user in users
        myuser = db.session.query(Users).filter_by(email=session["user"]["preferred_username"]).first()
        username = session["user"]["preferred_username"].split("@")[0]

        # if user is not found, log it into our DB
        if not myuser:
            temp_user = Users(username=session["user"]["preferred_username"].split("@")[0], email=session["user"]["preferred_username"],
                role='user', blocked=0, subscribed=0)
            db.session.add(temp_user)
            db.session.commit()
        return render_template('homepage.html', user=session["user"], version=msal.__version__, username=username)

@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    if session.get("user"):
        return redirect(url_for("index"))
    else:
        return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

'''
API call for MS graph
'''
@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)

'''
Media page for current blobs on storage
Function: Update copies available on blobs, 
'''
@app.route("/media")
def mediacall():
    # require user-login
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    else:
        username = session["user"]["preferred_username"].split("@")[0]

        blob_list = update_media()
        return render_template('media.html', blob_list=blob_list, username=username)


'''
transition page for user renting media
function: checks copies for availability then deduct copies if available
allows users to rent copies, copies are stored in metadata
rental also committed to rental log in SQL DB
'''
@app.route("/rental_auth/<container>/<blob>")
def rental_auth(container, blob):
    username = session["user"]["preferred_username"].split("@")[0]

    # establish BSC
    blob_service_client = BlobServiceClient.from_connection_string(app_config.AZURE_STORAGE_CONNECTION_STRING)

    # client for specific blob handling (the media we select on results page)
    blob_client = blob_service_client.get_blob_client(container=container, blob=blob)

    # setting metadata for copies available
    # blob_client.set_blob_metadata(metadata={'copies': '1'}) # this is hardcoded, eventually will be a feature for admins
    properties = blob_client.get_blob_properties()
    copies = int(properties.metadata['copies'])

    # check if media currently rented by user
    currently_rented = db.session.query(Rentals).filter(
        Rentals.rental_name == properties.name, 
        Rentals.email==session["user"]["preferred_username"], 
        Rentals.checked_in==0).all()

    # if there are any copies available and user does not currently have it rented, rent it
    if not currently_rented and copies > 0:
        copies -= 1
        blob_client.set_blob_metadata(metadata={'copies': str(copies)})
        temp = Rentals(rental_name=properties.name, email=session["user"]["preferred_username"],
            date_rented=datetime.now(), date_returned=datetime.now()+timedelta(minutes=5), checked_in=0)
        db.session.add(temp)
        db.session.commit()
        success = 1
        flash('Rented successfully')
        return render_template('rental_auth.html', blob=properties.name, success=success, username=username)
    else:
        success = 0
        flash('Rental failed')
        return render_template('rental_auth.html', blob=properties.name, success=success, username=username)


'''
Function: Page for rentals
'''
@app.route("/rentals/<rental_container>/<rental_name>", methods=['GET', 'POST'])
def my_rentals(rental_container, rental_name):
    # require user-login
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    else:
        username = session["user"]["preferred_username"].split("@")[0]

        # run update 
        blob_list = update_media()

        # get current rentals of the user
        currently_rented = db.session.query(Rentals).filter(
            Rentals.email==session["user"]["preferred_username"], 
            Rentals.checked_in==0).all()
        temp_rentals = []

        # restrict only those who have it rented
        for rental in currently_rented:
            print(str(rental))
            print(rental_name)
            if str(rental_name) == str(rental):
                temp_rentals += rental_name

        if temp_rentals:
            # generate url token to render pdf
            # TODO RESTRICT DOWNLOAD CAPABILITIES
            url_sas_token = get_url_with_container_sas_token(rental_container, rental_name)

            return render_template('rentals.html', pdf_url=url_sas_token, username=username)
        else:
            print('problem')
            return redirect(url_for("mediacall"))

'''
Profile page: here there be rentals and user info
'''
@app.route('/account')
def account():
    # require user login
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    else:
        username = session["user"]["preferred_username"].split("@")[0]

        # update the blob list
        blob_list = update_media()
        myRentals = []

        # get current rentals
        currently_rented = db.session.query(Rentals).filter(
            Rentals.email==session["user"]["preferred_username"], 
            Rentals.checked_in==0).all()

        # use current rentals of user to grab appropriate blob
        for blob in blob_list:
            for rental in currently_rented:
                if str(blob.name) == str(rental):
                    myRentals.append(blob)

        return render_template("account.html", username=username, user=session["user"], currently_rented=currently_rented, myRentals=myRentals)


'''
Function updates any media that is overdue by 
updating its checked_in status and number of copies
'''
def update_media():
    # establish connection with blobs and containers
    blob_service_client = BlobServiceClient.from_connection_string(app_config.AZURE_STORAGE_CONNECTION_STRING)
    
    # check db for "due" books currently in db by checked in and due date
    # due - date_returned is before the current time and hasn't been checked in
    check_due = db.session.query(Rentals).filter(Rentals.date_returned < datetime.now(), Rentals.checked_in == 0).all()

    # list all the containers in our resource
    all_containers=blob_service_client.list_containers(include_metadata=True)
    blob_list = []

    # loop through containers to list all available blobs
    for container in all_containers:
        container_client = ContainerClient.from_connection_string(app_config.AZURE_STORAGE_CONNECTION_STRING, container_name=container.name)
        temp=container_client.list_blobs()
        # loop through blobs in container
        for blob in temp:
            blob_client = blob_service_client.get_blob_client(container=container, blob=blob)
            properties = blob_client.get_blob_properties()

            # loop through due and see if any rendered blobs need to be checked-in
            for item in check_due:
                if properties.name == item.rental_name:

                    # update copies and check-in media
                    copies = int(properties.metadata['copies'])
                    copies += 1
                    blob_client.set_blob_metadata(metadata={'copies': str(copies)})

                    # update SQL DB 
                    my_rental = db.session.query(Rentals).filter(
                        Rentals.rental_name==properties.name, 
                        Rentals.date_returned < datetime.now(),
                        Rentals.checked_in==0
                        ).first()
                    my_rental.checked_in = 1
                    db.session.add(my_rental)
                    db.session.commit()
            blob_list.append(blob)
    return blob_list

# using generate_container_sas
def get_url_with_container_sas_token(container_name, blob_name):
    container_sas_token = generate_container_sas(
        account_name=app_config.ACCOUNT_NAME,
        container_name=container_name,
        account_key=app_config.ACCOUNT_KEY,
        permission=ContainerSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    blob_url_with_container_sas_token = f"https://{app_config.ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{blob_name}?{container_sas_token}"
    return blob_url_with_container_sas_token

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template

if __name__ == "__main__":
    app.run()






"""
This could be another method of logging in
"""
# @app.route("/")
# def splash():
#     return render_template("base.html")

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         email = form.email.data
#         password = form.password.data

#         user = db.session.query(Users).filter_by(email=email).first()

#         if user is not None and password == user.password:
#             flash('Login Successful')
#             return redirect(url_for('home'))
#     return render_template('login.html', form=form)

# @login_required
# @app.route('/home', methods=['GET', 'POST'])
# def home():
#     return render_template('homepage.html')
