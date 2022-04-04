
import quart 
import discord
import setup
import os
import urllib.parse
import random
import secrets
import logging
import typing
import json

from client import client, data
from web.oauth import Oauth
from web import encryption
from modules.tracking import classes as tracking_classes

from discord.ext import commands



async def generate_app(bot : commands.Bot, client : client.Client) -> quart.Quart:

    app = quart.Quart(__name__, template_folder=os.path.abspath("./web/templates"), static_folder=os.path.abspath("./web/static"))

    

    if setup.production:
        logging.getLogger('quart.serving').setLevel(logging.ERROR)

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

                user_cached = users[reuse_token]["user"]
                print(user_cached)
                user = client.bot.get_user(int(user_cached["id"])) if "id" in user_cached else None

                if user:
                    for key, value in user._to_minimal_user_json().items():
                        if key == "avatar" or key == "id":
                            continue
                        users[reuse_token]["user"][key] = value
                    

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
    
    @app.route("/api/commands", methods=["GET"])
    async def api_commands():

        modules = data.modules 

        for module_name in modules:

            for i, command_name in enumerate(modules[module_name]["commands"]):
                command = client.get_command(command_name)

                if not command:
                    continue

                options = [
                    {
                        "name":parameter.name, 
                        "description":parameter.description, 
                        "required":parameter.required, 
                        "min_value":parameter.min_value, 
                        "max_value":parameter.max_value,
                        "type":str(parameter.type.name)
                    } for parameter in command._params.values()
                ]

                modules[module_name]["commands"][i] = {
                    "name":command_name, 
                    "description":command.description,
                    "options":options
                }
        
        return quart.jsonify(modules)
    
    @app.route("/commands", methods=["GET"])
    async def commands():
        return await quart.render_template("commands.html", address=setup.address)

    @app.route("/dashboard", methods=["GET"])
    async def dashboard():
        if not quart.request.cookies.get('code'):
            return quart.redirect("/login?to=/dashboard")

        return await quart.render_template("dashboard.html", address=setup.address)

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
                return quart.jsonify({"error":True, "guild":await dashboard_home(guild, member), "message":"Missing permissions.", "data":await get_settings(guild)})

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
            return quart.jsonify({"error":True, "message":"Missing permissions.", "guild":await dashboard_home(guild, member), "data":await get_logs(guild)})

        await client.data.clear_logs(guild)

        await client.data.add_log(guild, member, "LOG_CLEAR", f"Logs were cleared by {member}")

        return quart.jsonify({"error":False, "message":"Successfully cleared logs", "data":await get_logs(guild)})

    async def dashboard_home(guild : discord.Guild, member : discord.Member):

        return {
            "modules": await client.data.get_modules(guild),
            "permissions":{"manage_guild":member.guild_permissions.manage_guild, "view_audit_logs":member.guild_permissions.view_audit_log},
            "channels":[{"name":channel.name, "id":str(channel.id), "type":channel.type[0]} for channel in guild.channels]
        }
    
    async def get_member(guild : discord.Guild, request) -> discord.Member:
        reuse_token = request.cookies.get("reuse_token")

        member : discord.Member = guild.get_member(int(users[reuse_token]["user"]["id"]))
        if not member:
            member : discord.Member = await guild.fetch_member(int(users[reuse_token]["user"]["id"]))

        return member

    @app.route("/api/dashboard/<path:guild_id>", methods=["GET"])
    async def dashboard_home_get(guild_id : int):
        
        guild = bot.get_guild(int(guild_id))
        
        member = await get_member(guild, quart.request)

        return quart.jsonify(await dashboard_home(guild, member))
    
    async def get_home(guild : discord.Guild):

        return {
            "modules": await client.data.get_modules(guild)
        }

    @app.route("/api/dashboard/<path:guild_id>/home", methods=["GET"])
    async def dashboard_get_home(guild_id : int):
        
        guild = bot.get_guild(int(guild_id))

        return quart.jsonify(await get_home(guild))
    
    async def get_tracking(guild : discord.Guild):

        g = tracking_classes.Guild(client, "all_time")

        disabledStats = await client.data.get_guild_setting(guild, "tracking_disabledStatistics")
        if not disabledStats:
            disabledStats = []

        return {
            "modules":await client.data.get_modules(guild), 
            "total_online":(await g.total_online(guild.members)).total_seconds(), 
            "disabled_statistics":disabledStats,
            "total_tracked":(await g.get_user(random.choice([m.id for m in guild.members if not m.bot]))).total_tracked().total_seconds()
        }
    
    @app.route("/api/dashboard/<path:guild_id>/tracking", methods=["GET"])
    async def dashboard_tracking(guild_id : int):

        guild = bot.get_guild(int(guild_id))

        tracking = await get_tracking(guild)

        return quart.jsonify(tracking)
    
    @app.route("/api/dashboard/<path:guild_id>/tracking", methods=["UPDATE"])
    async def save_tracking_settings(guild_id : int):

        data = await quart.request.json
        guild = bot.get_guild(int(guild_id))

        member = await get_member(guild, quart.request)

        returnValue = None

        if "enabled" in data:

            if not member.guild_permissions.manage_guild:
                return quart.jsonify({"error":True, "message":"Missing permissions.", "guild":await dashboard_home(guild, member), "data":await get_tracking(guild)})

            if data["enabled"] == True:
                await client.data.enable_module(guild, "tracking")
                await client.data.add_log(guild, member, "MODULE_ENABLED", f"{member} enabled module 'tracking'")

                return quart.jsonify({"error":False, "message":"Successfully enabled module", "data":await get_tracking(guild)})

            await client.data.disable_module(guild, "tracking")
            await client.data.add_log(guild, member, "MODULE_DISABLED", f"{member} disabled module 'tracking'")

            returnValue = quart.jsonify({"error":False, "message":"Successfully disabled module", "data":await get_tracking(guild)})
        
        if "disabledStatistics" in data:

            if not member.guild_permissions.manage_guild:
                return quart.jsonify({"error":True, "message":"Missing permissions.", "guild":await dashboard_home(guild, member), "data":await get_tracking(guild)})
            
            allowedStatistics = ["voice", "activity"]
            newStatisticsDisabled = []

            for stat in data["disabledStatistics"]:
                if stat in allowedStatistics:
                    newStatisticsDisabled.append(stat)
            
            await client.data.set_guild_setting(guild, "tracking_disabledStatistics", newStatisticsDisabled)
            await client.data.add_log(guild, member, "MODULE_UPDATED", f"{member} updated disabled statistics for module 'tracking'")
            
            returnValue = quart.jsonify({"error":False, "message":"Successfully set statistics toggles", "data":await get_tracking(guild)})

        
        return returnValue
    
    async def get_webhooks(guild : discord.Guild):

        return {
            "modules":await client.data.get_modules(guild), 
        }
    
    async def get_webhooks_in(channel : discord.TextChannel):

        msgs = await client.data.module_webhooks.get(channel)

        return {
            "messages":[{"webhook_id":str(m[2]), "message_id":str(m[3]), "message":json.loads(m[4])} for m in msgs]
        }
    
    @app.route("/api/dashboard/<path:guild_id>/webhooks", methods=["GET"])
    async def dashboard_webhooks(guild_id : int):

        guild = bot.get_guild(int(guild_id))

        tracking = await get_webhooks(guild)

        return quart.jsonify(tracking)
    
    @app.route("/api/dashboard/<path:guild_id>/webhooks/<path:channel_id>", methods=["GET"])
    async def dashboard_webhooks_channel(guild_id : int, channel_id : int):

        guild : discord.Guild = bot.get_guild(int(guild_id))
        channel = guild.get_channel(int(channel_id))

        tracking = await get_webhooks_in(channel)

        return quart.jsonify(tracking)
    
    @app.route("/api/dashboard/<path:guild_id>/webhooks/<path:channel_id>/<path:webhook_id>/<path:message_id>", methods=["DELETE"])
    async def delete_message(guild_id : int, channel_id : int, webhook_id : int, message_id : int):

        data = await quart.request.json
        guild = bot.get_guild(int(guild_id))
        channel = guild.get_channel(int(channel_id))

        member = await get_member(guild, quart.request)

        if not member.guild_permissions.manage_guild:
            return quart.jsonify({"error":True, "message":"Missing permissions.", "guild":await dashboard_home(guild, member), "data":await get_webhooks_in(channel)})

        await client.data.module_webhooks.delete(channel, webhook_id, message_id)

        return quart.jsonify({"error":False, "message":"Successfully deleted message", "data":await get_webhooks_in(channel)})
    
    @app.route("/api/dashboard/<path:guild_id>/webhooks/<path:channel_id>", methods=["POST"])
    async def post_message(guild_id : int, channel_id : int):

        data = await quart.request.json
        guild = bot.get_guild(int(guild_id))
        channel = guild.get_channel(int(channel_id))

        member = await get_member(guild, quart.request)

        if not member.guild_permissions.manage_guild:
            return quart.jsonify({"error":True, "message":"Missing permissions.", "guild":await dashboard_home(guild, member), "data":await get_webhooks_in(channel)})
        
        if "message" not in data:
            return quart.jsonify({"error":True, "message":"Message not attached (try reloading the page).", 
                    "guild":await dashboard_home(guild, member), "data":await get_webhooks_in(channel)})
        
        content = data["message"]["content"] if "content" in data["message"] and data["message"]["content"].replace(" ", "") != "" else None
        username = data["message"]["username"] if "username" in data["message"] and data["message"]["username"].replace(" ", "") != "" else None
        avatar_url = data["message"]["avatar_url"] if "avatar_url" in data["message"] and data["message"]["avatar_url"].replace(" ", "") != "" else None
        embeds : typing.List[discord.Embed] = []

        if "embeds" in data["message"]:
            for embed_raw in data["message"]["embeds"]:
                embed = discord.Embed(
                    title = embed_raw["title"] if "title" in embed_raw and embed_raw["title"].replace(" ", "") != "" else None,
                    description = embed_raw["description"] if "description" in embed_raw and embed_raw["description"].replace(" ", "") != "" else None
                )
                if "footer" in embed_raw and embed_raw["footer"].replace(" ", "") != "":
                    embed.set_footer(text=embed_raw["footer"])
                
                if embed.title or embed.description or embed.footer:
                    embeds.append(embed)
        
        if not content and len(embeds) == 0:
            return quart.jsonify({"error":True, "message":"Message content empty", "data":await get_webhooks_in(channel)})
        
        await client.data.module_webhooks.send(channel, username, avatar_url, content, embeds)

        return quart.jsonify({"error":False, "message":"Successfully sent webhook to channel.", "data":await get_webhooks_in(channel)})
        

    
    @app.route("/api/dashboard/<path:guild_id>/webhooks", methods=["UPDATE"])
    async def save_dashboard_webhooks(guild_id : int):

        data = await quart.request.json
        guild = bot.get_guild(int(guild_id))

        member = await get_member(guild, quart.request)

        returnValue = None

        if "enabled" in data:

            if not member.guild_permissions.manage_guild:
                return quart.jsonify({"error":True, "message":"Missing permissions.", "guild":await dashboard_home(guild, member), "data":await get_webhooks(guild)})

            if data["enabled"] == True:
                await client.data.enable_module(guild, "webhooks")
                await client.data.add_log(guild, member, "MODULE_ENABLED", f"{member} enabled module 'webhooks'")

                return quart.jsonify({"error":False, "message":"Successfully enabled module", "data":await get_webhooks(guild)})

            await client.data.disable_module(guild, "webhooks")
            await client.data.add_log(guild, member, "MODULE_DISABLED", f"{member} disabled module 'webhooks'")

            returnValue = quart.jsonify({"error":False, "message":"Successfully disabled module", "data":await get_webhooks(guild)})
        
        return returnValue
    

        

    return app