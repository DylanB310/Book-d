from azure.storage import blob
from werkzeug.utils import redirect
from app import app, db
from flask import render_template, url_for, request, session, flash, redirect
import msal
import copy
import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

import requests
from app import app_config

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    else:
        return render_template('homepage.html', user=session["user"], version=msal.__version__)

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

@app.route("/media")
def mediacall():
    # require user-login
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    else:
        # establish connection with blobs and containers
        blob_service_client = BlobServiceClient.from_connection_string(app_config.AZURE_STORAGE_CONNECTION_STRING)

        # list all the containers in our resource
        all_containers=blob_service_client.list_containers(include_metadata=True)
        temp_c=copy.copy(all_containers) # deep copy of all containers
        temp_b=[]

        for container in all_containers:
            container_client = blob_service_client.get_container_client(container.name)
            blob_list=container_client.list_blobs()
            temp_b.append(blob_list)

        return render_template('media.html', container_list=temp_c, blob_list=temp_b)


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
