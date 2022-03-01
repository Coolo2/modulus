import requests
import setup

import aiohttp

class Oauth(object):
    client_id = str(setup.application_id)
    client_secret = setup.client_secret
    scope = "identify%20guilds"
    redirect_uri = setup.address + "/return"
    discord_login_url = setup.invite_with_identify
    discord_token_url = "https://discord.com/api/oauth2/token"
    discord_api_url = "https://discord.com/api"

    @staticmethod
    async def get_access_token(code):
        payload = {
            'client_id': Oauth.client_id,
            'client_secret': Oauth.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': Oauth.redirect_uri,
            'scope': Oauth.scope
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url = Oauth.discord_token_url, data=payload, headers=headers) as r:
                json = await r.json()
                return json["access_token"]
    
    @staticmethod
    async def get_user_json(access_token):
        url = Oauth.discord_api_url+"/users/@me"
        headers = {
            'Authorization': "Bearer {}".format(access_token)
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as r:
                json = await r.json()
                return json
                