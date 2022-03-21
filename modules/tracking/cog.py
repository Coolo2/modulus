from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 

from discord import app_commands 
from discord.ext import commands 

import setup as s

from modules.tracking import classes, data

from client import errors

class SummaryCog(app_commands.Group, commands.Cog):
    def __init__(self, client : Client):
        self.client = client

        super().__init__(name="summary", description="Summarise tracking module")
    
    @app_commands.command(name="user", description="Get the tracking summary of a user")
    @app_commands.describe(user="A user to get the tracking summary for (defaults to yourself)")
    @app_commands.describe(timeframe="The timeframe of tracking to view")
    async def _user_command(
        self, 
        ctx : discord.Interaction | commands.Context, 
        user : discord.Member = None, 
        timeframe : typing.Literal["all time", "today", "week", "month"] = "All Time"
    ):

        if timeframe == "today":
            timeframe = "day"

        table = timeframe.replace(" ", "_").lower()

        if "tracking" not in await self.client.data.get_modules(ctx.guild):
            raise errors.MildError("Module **tracking** not enabled in this server.")

        author = user or (ctx.user if isinstance(ctx, discord.Interaction) else ctx.author)

        if await self.client.data.get_user_setting(author, "tracking_disabled"):
            raise errors.MildError(
                title="Tracking disabled", 
                description="This user has tracking **disabled**. Status summaries are not available to users who have tracking disabled.\nRe-enable it with **/tracking enable**"
            )

        guild = classes.Guild(self.client, table)
        user : classes.ParsedUser = await guild.get_user(author.id)

        embed = discord.Embed(title=f"User summary of {author} ({timeframe.title()})", color=s.embed)

        activities = ""

        for i, activity in enumerate(user.activities[:10]):
            activities += f"{i+1}. {activity.name} - **{classes.generate_time(activity.time.total_time)}** [{activity.time.last_seen.timestamp}]\n"

        embed.add_field(name="Statuses", value=f"""
Online: **{classes.generate_time(user.types.online.total_time)}** [{user.types.online.last_seen.timestamp}]
Do Not Disturb: **{classes.generate_time(user.types.dnd.total_time)}** [{user.types.dnd.last_seen.timestamp}]
Idle: **{classes.generate_time(user.types.idle.total_time)}** [{user.types.idle.last_seen.timestamp}]
Offline: **{classes.generate_time(user.types.offline.total_time)}** [{user.types.offline.last_seen.timestamp}]
        """)

        embed.add_field(name="Activities", value=activities if activities != "" else "_ _ ", inline=False)

        embed.add_field(name="Platforms", value=f"""
Desktop: **{classes.generate_time(user.platforms.desktop.total_time)}** [{user.platforms.desktop.last_seen.timestamp}]
Mobile: **{classes.generate_time(user.platforms.mobile.total_time)}** [{user.platforms.mobile.last_seen.timestamp}]
Web: **{classes.generate_time(user.platforms.web.total_time)}** [{user.platforms.web.last_seen.timestamp}]
        """)

        embed.add_field(name="More", value=f"""
Online : Idle : Offline - **{classes.ratioFunction(user.types.online.total_time + user.types.dnd.total_time, user.types.idle.total_time, user.types.offline.total_time)}**
Total tracked time: **{classes.generate_time(user.total_tracked())}**
        """, inline=False)
        
        if isinstance(ctx, discord.Interaction):
            return await ctx.response.send_message(embed=embed)
            
        return await ctx.reply(embed=embed, mention_author=False)
    
    

class TrackingCog(app_commands.Group, commands.Cog):
    def __init__(self, client : Client):
        self.client = client

        super().__init__(name="tracking", description="Enable and disable tracking for yourself")
    
    @app_commands.command(name="disable", description="Disable tracking")
    async def _disable(self, ctx : discord.Interaction | commands.Context):

        author = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author

        if await self.client.data.get_user_setting(author, "tracking_disabled"):
            raise errors.MildError("Enable it with **/tracking enable**", title="Tracking is already disabled")
        else:

            await self.client.data.set_user_setting(author, "tracking_disabled", True)

            embed = discord.Embed(
                title="Tracking disabled", 
                description="Tracking successfully **disabled**. Your status will no longer be tracked for server-specific analytics.", 
                color=s.embedSuccess
            )
            embed.set_footer(text="The Modulus team will never read any tracking data. It is purely for user information.")

        if isinstance(ctx, discord.Interaction):
            return await ctx.response.send_message(embed=embed)
        return await ctx.reply(embed=embed, mention_author=False)
    
    @app_commands.command(name="enable", description="Enable tracking")
    async def _enable(self, ctx : discord.Interaction | commands.Context):

        author = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author

        if not await self.client.data.get_user_setting(author, "tracking_disabled"):
            raise errors.MildError("Disable it with **/tracking disable**", title="Tracking is already disabled")
        else:

            await self.client.data.set_user_setting(author, "tracking_disabled", False)

            embed = discord.Embed(
                title="Tracking re-enabled", 
                description="Tracking successfully **enabled**. Your status will now be tracked for user-information (**/summary user**).", 
                color=s.embedSuccess
            )
            embed.set_footer(text="The Modulus team will never read any tracking data. It is purely for user information.")

        if isinstance(ctx, discord.Interaction):
            return await ctx.response.send_message(embed=embed)
        return await ctx.reply(embed=embed, mention_author=False)

async def setup(bot : commands.Bot):
    await bot.add_cog(SummaryCog(bot.client), guild=s.slash_guild)
    await bot.add_cog(TrackingCog(bot.client), guild=s.slash_guild)