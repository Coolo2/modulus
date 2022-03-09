import quart 
import discord
from discord.ext import commands
import setup
import os
import urllib.parse

from client import client

from web.oauth import Oauth
from web import encryption

async def generate_app(bot : commands.Bot, client : client.Client) -> quart.Quart:

    app = quart.Quart(__name__, template_folder=os.path.abspath("./web/templates"), static_folder=os.path.abspath("./web/static"))

    users = {}
    userGuilds = {}

    if setup.production == False:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        app.config["TEMPLATES_AUTO_RELOAD"] = True

    @app.route("/", methods=["GET"])
    async def index():
        return await quart.render_template("index.html", address=setup.address)
    
    @app.route("/invite", methods=["GET"])
    async def invite():
        gd = ""

        if "guild_id" in dict(quart.request.args):

            gd = f"&guild_id={quart.request.args['guild_id']}"

        resp = await quart.make_response(quart.redirect(setup.invite_with_identify + gd))

        if "to" in quart.request.args:
            resp.set_cookie("redirectTo", urllib.parse.quote(quart.request.args["to"]))

        return resp
    
    @app.route("/login", methods=["GET"])
    async def login():
        
        resp = await quart.make_response(quart.redirect(setup.identify))

        if "to" in quart.request.args:
            resp.set_cookie("redirectTo", urllib.parse.quote(quart.request.args["to"]))

        return resp
    
    @app.route("/logout", methods=["GET"])
    async def logout():

        resp = await quart.make_response(quart.redirect("/"))

        resp.delete_cookie("code")

        return resp
    
    @app.route("/api/user/guilds", methods=["GET"])  
    async def user_guilds():
        code = quart.request.cookies.get('code')

        if not code:
            return quart.jsonify({"error":"Not Logged In"})

        if code in userGuilds:
            if "guilds" in userGuilds[code]:
                return quart.jsonify(userGuilds[code]["guilds"])

        access = await Oauth.refresh_token(code)

        if "error" in access:
            return quart.jsonify({"error":"Login invalid"})

        guild_json = await Oauth.get_user_guilds(access["access_token"])

        for i, guild_data in enumerate(guild_json):
            for guild in bot.guilds:
                if int(guild_data["id"]) == guild.id:
                    guild_json[i]["in"] = True 
                    
            if "in" not in guild_json[i]:
                guild_json[i]["in"] = False 

        userGuilds[ access["refresh_token"] ] = {"access":access, "guilds":guild_json}

        resp = await quart.make_response(quart.jsonify(guild_json))
        resp.set_cookie("code", access["refresh_token"], max_age=8_760*3600)

        return resp

    @app.route("/api/user", methods=["GET"])  
    async def userinfo():
        code = quart.request.cookies.get('code')

        if not code:
            return quart.jsonify({"error":"Not Logged In"})

        if code in users:
            if "user" in users[code]:
                return quart.jsonify(users[code]["user"])

        access = await Oauth.refresh_token(code)

        if "error" in access:
            print(access)
            return quart.jsonify({"error":"Login invalid"})

        user_json = await Oauth.get_user_json(access["access_token"])

        users[ access["refresh_token"] ] = {"access":access, "user":user_json}

        resp = await quart.make_response(quart.jsonify(user_json))
        resp.set_cookie("code", access["refresh_token"], max_age=8_760*3600)

        return resp


    @app.route("/return", methods=["GET"])  
    async def discord_return():

        if "error" in quart.request.args:
            return quart.redirect("/")

        code = quart.request.args['code']
        access = await Oauth.get_access_token(code)

        users[ access["refresh_token"] ] = {"access":access}

        url = "/"
        if "redirectTo" in quart.request.cookies:
            url = quart.request.cookies.get("redirectTo")

        resp = await quart.make_response(quart.redirect(url))

        if url != "/":
            resp.delete_cookie("redirectTo")

        resp.set_cookie("code", access["refresh_token"], max_age=8_760*3600)

        return resp

    @app.route("/dashboard", methods=["GET"])
    async def dashboard():
        

        return await quart.render_template("dashboard.html")

    @app.route("/dashboard/<path:id>", methods=["GET"])
    async def dashboard_with_id(id):
        

        return await quart.render_template("dashboard.html")
    
    @app.route("/api/dashboard/<path:guild_id>/settings", methods=["GET"])
    async def dashboard_settings(guild_id : int):

        print(guild_id)

        guild = bot.get_guild(int(guild_id))
        prefix = await client.data.get_prefix(guild)

        return quart.jsonify({"prefix":prefix})
        
        

    return app