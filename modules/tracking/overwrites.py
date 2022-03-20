
from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 

from aiostream import stream, pipe

from modules.tracking import data

async def task(client : Client):
    
    cursor = await client.file.db.db.execute("SELECT guild_id FROM modules WHERE modules LIKE '%tracking%'")
    all_guilds = await cursor.fetchall()

    users_checked : typing.List[data.User] = []

    async for guild_id in stream.iterate(all_guilds) | pipe.map(lambda x: x[0]):
        
        guild : discord.Guild = client.bot.get_guild(guild_id)

        for member in guild.members:
            if not member.bot:
                user = await client.data.module_tracking.get_user("all_time", member.id)
                await user.add_type(member.status.name)

                users_checked.append(user)
    
    for track_user in users_checked:
        await track_user.save()
    
    del users_checked