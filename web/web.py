import quart 
import discord
import setup
import os

from web.oauth import Oauth
from web import encryption

async def generate_app(bot : discord.Bot) -> quart.Quart:

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
        return quart.redirect(setup.invite_with_identify)
    
    @app.route("/login", methods=["GET"])
    async def login():
        return quart.redirect(setup.identify)
    
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

        userGuilds[ access["refresh_token"] ] = {"access":access, "guilds":guild_json}

        resp = await quart.make_response(quart.jsonify(guild_json))
        resp.set_cookie("code", access["refresh_token"])

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
            return quart.jsonify({"error":"Login invalid"})

        user_json = await Oauth.get_user_json(access["access_token"])

        users[ access["refresh_token"] ] = {"access":access, "user":user_json}

        resp = await quart.make_response(quart.jsonify(user_json))
        resp.set_cookie("code", access["refresh_token"])

        return resp


    @app.route("/return", methods=["GET"])  
    async def discord_return():

        if "error" in quart.request.args:
            return quart.redirect("/")

        code = quart.request.args['code']
        access = await Oauth.get_access_token(code)

        users[ access["refresh_token"] ] = {"access":access}

        resp = await quart.make_response(quart.redirect("/"))
        resp.set_cookie("code", access["refresh_token"])

        return resp
    
    @app.route("/dashboard", methods=["GET"])
    async def dashboard():
        

        return quart.redirect("/")
        

    return app