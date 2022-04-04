
import discord 

from discord.ext import commands



class en:
    name = "en"
    fullName = "English"

    def __init__(self, *args, **kwargs):
        arg1 = args[0] if len(args) > 0 else None
        arg2 = args[1] if len(args) > 1 else None
        arg3 = args[2] if len(args) > 2 else None
        arg4 = args[3] if len(args) > 3 else None
        arg5 = args[4] if len(args) > 4 else None

        self.help = "help"
        self.help_description = "Get help for the bot and list its commands"

        self.description = "Modulus is a module based Discord bot which is one of the must customizable out there."
        self.owned_description = "It is owned by **Coolo2#5499** and was released on XXXX"
        self.bot_help = "Bot help"
        self.commands = "Commands"
        self.use_button = "Use the button below to see the bot's commands"
        self.view_commands = "View commands"
    
    def g(self):
        return self

languages = [en]

def get(ctx : discord.Interaction | commands.Context) -> en:

    locale = None

    if isinstance(ctx, discord.Interaction):
        locale = ctx.guild_locale
    else:
        locale = ctx.guild.preferred_locale
    
    for language in languages:
        if language.name in str(locale):
            return language()