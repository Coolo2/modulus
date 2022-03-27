from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 
import math
import datetime

from discord import app_commands 
from discord.ext import commands 

import setup as s

from modules.tracking import classes, data, spotify as sp

from client import errors

class SummaryCog(app_commands.Group, commands.Cog):
    def __init__(self, client : Client):
        self.client = client

        super().__init__(name="summary", description="Summarise tracking module")
    
    @app_commands.command(name="spotify", description="Get spotify statistics for yourself or another user")
    @app_commands.describe(user="A user to get the tracking summary for (defaults to yourself)")
    @app_commands.describe(timeframe="The timeframe of tracking to view")
    async def _spotify_command(
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
        spotify = self.client.data.module_tracking.spotify 

        embed = discord.Embed(title=f"Spotify summary for {author} ({timeframe.title()})", color=s.embed)

        artists = ""
        tracks_msg = ""

        for i, artist in enumerate(user.artists[:10]):
            artists += f"{i+1}. {artist.name} - **{classes.generate_time(artist.total_listened)}**\n"
        
        embed.add_field(name="Artists", value=artists[:1024] if artists != "" else "This user has never shown spotify on their status in this timeframe", inline=False)
        if artists != "":
            embed.add_field(name="Tracks", value="<a:typing:957263956605542450>", inline=False)

        m = await self.client.send(ctx, embed=embed)
        if artists == "":
            return
        message = await self.client.original_message(ctx, m)

        # Requests

        trackFeatures = await spotify.get_track_details(await spotify.get_track_features(user.tracks))

        averageTempo = 0
        averagePopularity = 0
        averageDuration = 0
        averages = {"energy":0, "danceability":0, "valence":0, "instrumentalness":0, "liveness":0, "acousticness":0, "speechiness":0}
        for track in trackFeatures:
            if track.features:
                averageTempo += track.features.tempo

                for average in averages:
                    averages[average] += getattr(track.features, average)
        
        for track in trackFeatures:
            averagePopularity += track.popularity
            averageDuration += track.duration
        
        averageTempo /= len(trackFeatures)
        averagePopularity /= len(trackFeatures)
        averageDuration /= len(trackFeatures)
        for avg in averages:
            averages[avg] /=  len(trackFeatures)
        averages = dict(sorted(averages.items(), key=lambda item: item[1], reverse=True))

        embed.add_field(name="Average Tempo (BPM)", value=str(round(averageTempo)))
        embed.add_field(name="Average Song Popularity", value=f"{round(averagePopularity)}*")
        embed.add_field(name="Average Song Length", 
            value=f"{math.floor(averageDuration / 1000 / 60)}:{str(round((averageDuration / 1000) % 60)).zfill(2)}"
        )

        songFeatures = ""
        counter = 0
        for avg in averages:
            counter += 1
            songFeatures += f"{counter}. {avg.title()} - **{round(averages[avg] * 100)}%**\n"
        
        embed.add_field(name="Average Song Features", value=songFeatures, inline=False)

        artists = ""
        artists_dict : typing.Dict[str, sp.Artist] = {}
        for track in trackFeatures:
            for artist in track.artists:
                if artist.name in [a.name for a in user.artists]:
                    artist.total_listened = user.artists[[a.name for a in user.artists].index(artist.name)].total_listened
                    
                artists_dict[artist.name] = artist 
        artists_dict = dict(sorted(artists_dict.items(), key=lambda item: item[1].total_listened, reverse=True))
        
        for i, artist in enumerate(list(artists_dict.values())[:10]):
            artist : sp.Artist = artist
            artists += f"{i+1}. [{artist.name}]({artist.url}) - **{classes.generate_time(artist.total_listened)}**\n"

        for i, track in enumerate(trackFeatures[:8]):
            tracks_msg += f"{i+1}. [{', '.join([a.name for a in track.artists])} - {track.name}]({track.url}) - **{classes.generate_time(track.total_listened)}**\n"
        
        embed.remove_field(0)
        embed.remove_field(0)
        embed.add_field(name="Artists", value=artists[:1024] if artists != "" else "This user has never shown spotify on their status in this timeframe", inline=False)
        embed.add_field(name="Tracks", value=tracks_msg[:1024] if tracks_msg != "" else "This user has never shown spotify on their status in this timeframe")

        embed.set_footer(text="*Song popularity is a number based on plays and song release date. More recent and more played songs have a higher popularity number.")

        await message.edit(embed=embed)


    
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

        voice = ""

        for i, voice_channel in enumerate(user.voice_channels[:5]):
            voice += f"{i+1}. <#{voice_channel.channel_id}> - **{classes.generate_time(voice_channel.time.total_time)}** [{voice_channel.time.last_seen.timestamp}]"

        st = await self.client.data.get_guild_setting(ctx.guild, "tracking_disabledStatistics")

        embed.add_field(name="Statuses", value=f"""
Online: **{classes.generate_time(user.types.online.total_time)}** [{user.types.online.last_seen.timestamp}]
Do Not Disturb: **{classes.generate_time(user.types.dnd.total_time)}** [{user.types.dnd.last_seen.timestamp}]
Idle: **{classes.generate_time(user.types.idle.total_time)}** [{user.types.idle.last_seen.timestamp}]
Offline: **{classes.generate_time(user.types.offline.total_time)}** [{user.types.offline.last_seen.timestamp}]
        """)
        
        if not st or "activity" not in st:
            embed.add_field(name="Activities", value=activities if activities != "" else "_ _ ", inline=False)

        embed.add_field(name="Platforms", value=f"""
Desktop: **{classes.generate_time(user.platforms.desktop.total_time)}** [{user.platforms.desktop.last_seen.timestamp}]
Mobile: **{classes.generate_time(user.platforms.mobile.total_time)}** [{user.platforms.mobile.last_seen.timestamp}]
Web: **{classes.generate_time(user.platforms.web.total_time)}** [{user.platforms.web.last_seen.timestamp}]
        """, inline=False)

        
        if not st or "voice" not in st:
            embed.add_field(name="Voice", value=voice if voice != "" else "_ _ ", inline=False)

        embed.add_field(name="More", value=f"""
Online : Idle : Offline - **{classes.ratioFunction(user.types.online.total_time + user.types.dnd.total_time, user.types.idle.total_time, user.types.offline.total_time)}**
Total tracked time: **{classes.generate_time(user.total_tracked())}**
        """, inline=False)
        
        if isinstance(ctx, discord.Interaction):
            return await ctx.response.send_message(embed=embed)
            
        return await ctx.reply(embed=embed, mention_author=False)
    
    @app_commands.command(name="server", description="Get a summary of tracking statistics for every user in the server you are in")
    @app_commands.describe(timeframe="The timeframe of tracking to view")
    async def _server_command(
        self, 
        ctx : discord.Interaction | commands.Context, 
        timeframe : typing.Literal["all time", "today", "week", "month"] = "All Time"
    ):
        if timeframe == "today":
            timeframe = "day"
        table = timeframe.replace(" ", "_").lower()

        if "tracking" not in await self.client.data.get_modules(ctx.guild):
            raise errors.MildError("Module **tracking** not enabled in this server.")

        author = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author

        guild = classes.Guild(self.client, table)

        embed = discord.Embed(title=f"Server tracking summary ({timeframe.title()})", color=s.embed)

        users = await guild.users_from_members(ctx.guild.members)

        totalOnline = datetime.timedelta()
        # {"activity_name":{"total":0, "users":[discord.User() ...]}}
        activities = {}
        totalTracked = datetime.timedelta()

        for user in users:
            totalTracked = user.total_tracked()
            total_online_user = (user.types.online.total_time + user.types.dnd.total_time) 
            totalOnline += total_online_user

            for activity in user.activities:
                if activity.name not in activities:
                    activities[activity.name] = {"total":datetime.timedelta(), "users":[]}
                
                activities[activity.name]["total"] += activity.time.total_time
                activities[activity.name]["users"].append({"user":user, "time":activity.time.total_time})
        
        activities = dict(sorted(activities.items(), key=lambda x: x[1]["total"], reverse=True)[:10])

        activities_msg = ""
        statuses_msg = ""
        

        for i, (activityName, activity) in enumerate(activities.items()):
            top_activities_user = {"id":None, "time":datetime.timedelta()}
            
            for user in activity["users"]:
                if user["time"] > top_activities_user["time"]:
                    top_activities_user = {"id":user["user"].user.user_id, "time":user["time"], "percentage":round((user["time"]/activity["total"]) * 100)}
            
            activities_msg += f"{i+1}. {activityName} - **{classes.generate_time(activity['total'])}** (<@{top_activities_user['id']}> `{classes.generate_time(top_activities_user['time'])}` **{top_activities_user['percentage']}%**)\n"

        for i, user in enumerate(sorted(users, key=lambda x: x.types.online.total_time + x.types.dnd.total_time, reverse=True)[:10]):
            
            
            last_online = None 

            if user.types.dnd.last_seen.time and user.types.online.last_seen.time:
                last_online = user.types.dnd.last_seen.timestamp if user.types.dnd.last_seen.time > user.types.online.last_seen.time else user.types.online.last_seen.timestamp
            elif user.types.dnd.last_seen.time:
                last_online = user.types.dnd.last_seen.timestamp
            else:
                last_online = user.types.online.last_seen.timestamp

            statuses_msg += f"{i+1}. <@{user.user.user_id}> - **{classes.generate_time(user.types.dnd.total_time + user.types.online.total_time)}** [{last_online}]\n"

        st = await self.client.data.get_guild_setting(ctx.guild, "tracking_disabledStatistics")

        if not st or "activity" not in st:
            embed.add_field(name="Activities", value=activities_msg, inline=False)
        embed.add_field(name="Online Time", value=statuses_msg if statuses_msg != "" else "_ _ ", inline=False)

        embed.add_field(name="More", value=f"""
Total Online Time - **{classes.generate_time(totalOnline)}**
Total Tracked Time - **{classes.generate_time(totalTracked)}**

        """, inline=False)

        await self.client.send(ctx, embed=embed)
    

class TrackingCog(app_commands.Group, commands.Cog):
    def __init__(self, client : Client):
        self.client = client

        super().__init__(name="tracking", description="Enable and disable tracking for yourself")
    
    @app_commands.command(name="disable", description="Disable tracking")
    async def _disable(self, ctx : discord.Interaction | commands.Context):

        author = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author

        if await self.client.data.get_user_setting(author, "tracking_disabled"):
            raise errors.MildError("Enable it with **/tracking enable**", title="Tracking is already disabled")

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