import os
import json
import boto3
import requests
from fastapi import Depends, APIRouter, Request
from fastapi.security.api_key import APIKeyCookie
from ..utils import require_auth

router = APIRouter(tags=["AWS"])
cookie_scheme = APIKeyCookie(name="token")

AWS_ROLE_ARN = os.getenv("AWS_ROLE_ARN")

@router.get("/aws/cli", dependencies=[Depends(cookie_scheme)])
async def aws_cli(request: Request, token: dict = Depends(require_auth)):
    session = request.app.state.sessions[token['session']]
    return get_aws_credentials(session['id_token'])

@router.get("/aws/console")
async def aws_console(request: Request, token: dict = Depends(require_auth)):
    session = request.app.state.sessions[token['session']]
    creds = get_aws_credentials(session['id_token'])
    login_url = get_console_login_url(creds)
    return {"url": login_url}


def get_aws_credentials(id_token: str):
    sts_client = boto3.client("sts")
    response = sts_client.assume_role_with_web_identity(
        RoleArn=AWS_ROLE_ARN,
        RoleSessionName="fastapi-google-aws", # can be anything. Used to identify the session.
        WebIdentityToken=id_token,
        DurationSeconds=3600,
    )
    creds = response["Credentials"]
    return creds

def get_console_login_url(creds):
    session_json = json.dumps({
        "sessionId": creds["AccessKeyId"],
        "sessionKey": creds["SecretAccessKey"],
        "sessionToken": creds["SessionToken"]
    })

    # Get signin token
    r = requests.get("https://signin.aws.amazon.com/federation", params={"Action": "getSigninToken", "Session": session_json})
    signin_token = r.json()["SigninToken"]

    # Construct login URL
    destination = "https://console.aws.amazon.com"
    login_url = f"https://signin.aws.amazon.com/federation?Action=login&Issuer=MyApp&Destination={destination}&SigninToken={signin_token}"
    return login_url
