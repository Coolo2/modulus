from calendar import c
import quart 
import discord
from discord.ext import commands
import setup
import os
import urllib.parse

import random
import secrets

from client import client

from web.oauth import Oauth
from web import encryption

from modules.tracking import classes as tracking_classes

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
        resp.delete_cookie("reuse_token")
        resp.delete_cookie("reuse_token_guild")

        return resp
    
    @app.route("/api/user/guilds", methods=["GET"])  
    async def user_guilds():
        code = quart.request.cookies.get('code')
        reuse_token = quart.request.cookies.get("reuse_token_guild")

        if reuse_token in userGuilds and quart.request.args.get("refresh") != "true" :
            if "guilds" in userGuilds[reuse_token]:
                return quart.jsonify(userGuilds[reuse_token]["guilds"])

        access = await Oauth.refresh_token(code)

        if "error" in access:
            return quart.jsonify({"error":"Login invalid"})

        rt = secrets.token_urlsafe(16)
        guild_json = await Oauth.get_user_guilds(access["access_token"])

        for i, guild_data in enumerate(guild_json):
            for guild in bot.guilds:
                if int(guild_data["id"]) == guild.id:
                    guild_json[i]["in"] = True 
                    
            if "in" not in guild_json[i]:
                guild_json[i]["in"] = False 

        userGuilds[ rt ] = {"access":access, "guilds":guild_json}

        resp = await quart.make_response(quart.jsonify(guild_json))
        resp.set_cookie("code", access["refresh_token"], max_age=8_760*3600)
        resp.set_cookie("reuse_token_guild", rt, max_age=8_760*3600)

        return resp

    @app.route("/api/user", methods=["GET"])  
    async def userinfo():
        
        code = quart.request.cookies.get('code')
        reuse_token = quart.request.cookies.get("reuse_token")

        if not code:
            return quart.jsonify({"error":"Not Logged In"})

        if reuse_token in users:
            if "user" in users[reuse_token]:
                return quart.jsonify(users[reuse_token]["user"])
        
        rt = secrets.token_urlsafe(16)
        access = await Oauth.refresh_token(code)

        if "error" in access:
            return quart.jsonify({"error":"Login invalid"})

        user_json = await Oauth.get_user_json(access["access_token"])

        users[rt] = {"access":access, "user":user_json}

        resp = await quart.make_response(quart.jsonify(user_json))
        resp.set_cookie("code", access["refresh_token"], max_age=8_760*3600)
        resp.set_cookie("reuse_token", rt, max_age=8_760*3600)

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
        if not quart.request.cookies.get('code'):
            return quart.redirect("/login?to=/dashboard")

        return await quart.render_template("dashboard.html")

    @app.route("/dashboard/<path:guild_id>", methods=["GET"])
    async def dashboard_with_id(guild_id):

        if not quart.request.cookies.get('code'):
            return quart.redirect(f"/login?to=/dashboard/{guild_id}")

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

        member = await get_member(guild, quart.request)

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

        member = await get_member(guild, quart.request)

        if not member.guild_permissions.manage_guild:
            return quart.jsonify({"error":True, "message":"Missing permissions."})

        await client.data.clear_logs(guild)

        await client.data.add_log(guild, member, "LOG_CLEAR", f"Logs were cleared by {member}")

        return quart.jsonify({"error":False, "message":"Successfully cleared logs", "data":await get_logs(guild)})

    async def dashboard_home(guild : discord.Guild, member : discord.Member):

        return {
            "modules": await client.data.get_modules(guild),
            "permissions":{"manage_guild":member.guild_permissions.manage_guild}
        }
    
    async def get_member(guild, request) -> discord.Member:
        reuse_token = request.cookies.get("reuse_token")

        member : discord.Member = await guild.fetch_member(int(users[reuse_token]["user"]["id"]))

        return member

    @app.route("/api/dashboard/<path:guild_id>", methods=["GET"])
    async def dashboard_home_get(guild_id : int):
        
        guild = bot.get_guild(int(guild_id))
        
        member = await get_member(guild, quart.request)

        return quart.jsonify(await dashboard_home(guild, member))
    
    async def get_tracking(guild : discord.Guild):

        g = tracking_classes.Guild(client, "all_time")

        return {
            "modules":await client.data.get_modules(guild), 
            "total_online":(await g.total_online(guild.members)).total_seconds(), 
            "total_tracked":(await g.get_user(random.choice([m.id for m in guild.members if not m.bot]))).total_tracked().total_seconds()
        }
    
    @app.route("/api/dashboard/<path:guild_id>/tracking", methods=["GET"])
    async def dashboard_tracking(guild_id : int):

        guild = bot.get_guild(int(guild_id))

        tracking = await get_tracking(guild)

        return quart.jsonify(tracking)
    
    @app.route("/api/dashboard/<path:guild_id>/tracking", methods=["POST"])
    async def save_tracking_settings(guild_id : int):

        data = await quart.request.json
        guild = bot.get_guild(int(guild_id))

        member = await get_member(guild, quart.request)

        if "enabled" in data:

            if not member.guild_permissions.manage_guild:
                return quart.jsonify({"error":True, "message":"Missing permissions."})

            if data["enabled"] == True:
                await client.data.enable_module(guild, "tracking")
                await client.data.add_log(guild, member, "MODULE_ENABLED", f"{member} enabled module 'tracking'")

                return quart.jsonify({"error":False, "message":"Successfully enabled module", "data":await get_tracking(guild)})

            await client.data.disable_module(guild, "tracking")
            await client.data.add_log(guild, member, "MODULE_DISABLED", f"{member} disabled module 'tracking'")

            return quart.jsonify({"error":False, "message":"Successfully disabled module", "data":await get_tracking(guild)})
    

        

    return app