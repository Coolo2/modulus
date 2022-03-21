
from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 
import datetime

from aiostream import stream, pipe
from modules.tracking import data

async def task(client : Client):

    if not await client.file.db.table_exists("settings"):
        await client.file.db.db.execute("CREATE TABLE settings(guild_id INTEGER, settings STRING, modules STRING)")
    
    cursor = await client.file.db.db.execute("SELECT guild_id FROM settings WHERE modules LIKE '%tracking%'")
    all_guilds = await cursor.fetchall()

    await client.data.module_tracking.do_timeframes()
    
    for timeframe in client.data.module_tracking.timeframes:

        users_checked : typing.List[data.User] = []

        async for guild_id in stream.iterate(all_guilds) | pipe.map(lambda x: x[0]):
            
            guild : discord.Guild = client.bot.get_guild(guild_id)

            for member in guild.members:
                
                if not member.bot:

                    platforms = {"desktop":member.desktop_status, "mobile":member.mobile_status, "web":member.web_status}
                    user = None

                    if any(u.user_id == member.id for u in users_checked):
                        for u in users_checked:
                            if u.user_id == member.id:
                                user = u
                    else:
                        if not await client.data.get_user_setting(member, "tracking_disabled"):

                            user = await client.data.module_tracking.get_user(timeframe, member.id)

                            await user.add_type(member.status.name)
                            
                            for activity in member.activities:
                                await user.add_activity(activity.name)
                            
                            for p_name, p_value in platforms.items():
                                if p_value.name != "offline":
                                    await user.add_platform(p_name)

                    if user:
                        users_checked.append(user)
        
        for track_user in users_checked:
            await track_user.save()
        
    
    del users_checked