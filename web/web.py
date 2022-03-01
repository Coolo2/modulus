import quart 
import discord
import setup
import os

from web.oauth import Oauth
from web import encryption

async def generate_app(bot : discord.Bot) -> quart.Quart:

    app = quart.Quart(__name__, template_folder=os.path.abspath("./web/templates"), static_folder=os.path.abspath("./web/static"))

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
    
    @app.route("/return", methods=["GET"])  
    async def discord_return():

        code = quart.request.args['code']
        access_token = await Oauth.get_access_token(code)
        user_json = await Oauth.get_user_json(access_token)

        print(user_json)

        return quart.redirect("/")
        

    return app