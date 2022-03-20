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
    
    async def get_settings(guild : discord.Guild):

        prefix = await client.data.get_prefix(guild)

        return {"prefix":prefix}

    
    @app.route("/api/dashboard/<path:guild_id>/settings", methods=["GET"])
    async def dashboard_settings(guild_id : int):

        guild = bot.get_guild(int(guild_id))

        settings = await get_settings(guild)

        return quart.jsonify(settings)
        
    
    @app.route("/api/dashboard/<path:guild_id>/settings", methods=["POST"])
    async def save_dashboard_settings(guild_id : int):

        data = await quart.request.json
        guild = bot.get_guild(int(guild_id))

        member : discord.Member = await guild.fetch_member(int(data["user"]))

        if "prefix" in data:

            if not member.guild_permissions.manage_guild:
                return quart.jsonify({"error":True, "message":"Missing permissions."})

            if len(data["prefix"]) > 10:
                return quart.jsonify({"error":True, "message":"Prefix too long."})
            
            if data["prefix"].replace(" ", "") == "":
                data["prefix"] = setup.default_prefix
            
            if data["prefix"] == await client.data.get_prefix(guild):
                return quart.jsonify({"error":True, "message":"Prefix not changed.", "data":await get_settings(guild)})

            await client.data.set_prefix(guild, data["prefix"])

            await client.data.add_log(guild, member, "PREFIX_SET", f"{member} set server prefix to {data['prefix']}")

            return quart.jsonify({"error":False, "message":"Successfully set prefix", "data":await get_settings(guild)})
    
    async def get_logs(guild : discord.Guild):

        logs = await client.data.get_logs(guild)

        return [log.to_dict() for log in logs]
    
    @app.route("/api/dashboard/<path:guild_id>/logs", methods=["GET"])
    async def dashboard_logs(guild_id : int):

        guild = bot.get_guild(int(guild_id))

        logs = await get_logs(guild)

        return quart.jsonify(logs)
    
    @app.route("/api/dashboard/<path:guild_id>/logs", methods=["DELETE"])
    async def clear_dashboard_logs(guild_id : int):
        data = await quart.request.json
        guild = bot.get_guild(int(guild_id))

        member : discord.Member = await guild.fetch_member(int(data["user"]))

        if not member.guild_permissions.manage_guild:
            return quart.jsonify({"error":True, "message":"Missing permissions."})

        await client.data.clear_logs(guild)

        return quart.jsonify({"error":False, "message":"Successfully cleared logs", "data":await get_logs(guild)})

    async def dashboard_home(guild : discord.Guild):

        return {"modules": await client.data.get_modules(guild)}

    @app.route("/api/dashboard/<path:guild_id>", methods=["GET"])
    async def dashboard_home_get(guild_id : int):
        
        guild = bot.get_guild(int(guild_id))

        return quart.jsonify(await dashboard_home(guild))
    
    async def get_tracking(guild : discord.Guild):
        
        return {"modules":await client.data.get_modules(guild)}
    
    @app.route("/api/dashboard/<path:guild_id>/tracking", methods=["GET"])
    async def dashboard_tracking(guild_id : int):

        guild = bot.get_guild(int(guild_id))

        tracking = await get_tracking(guild)

        return quart.jsonify(tracking)
    
    @app.route("/api/dashboard/<path:guild_id>/tracking", methods=["POST"])
    async def save_tracking_settings(guild_id : int):

        data = await quart.request.json
        guild = bot.get_guild(int(guild_id))

        member : discord.Member = await guild.fetch_member(int(data["user"]))

        if "enabled" in data:

            if not member.guild_permissions.manage_guild:
                return quart.jsonify({"error":True, "message":"Missing permissions."})

            if data["enabled"] == True:
                await client.data.enable_module(guild, "tracking")
                await client.data.add_log(guild, member, "MODULE_ENABLED", f"{member} enabled module 'tracking'")

                return quart.jsonify({"error":False, "message":"Successfully enabled module", "data":await get_tracking(guild)})
            else:
                await client.data.disable_module(guild, "tracking")
                await client.data.add_log(guild, member, "MODULE_DISABLED", f"{member} disabled module 'tracking'")

                return quart.jsonify({"error":False, "message":"Successfully disabled module", "data":await get_tracking(guild)})
        

    return app