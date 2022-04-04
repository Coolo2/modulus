

from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import datetime
import json
import discord

class DataModule():
    def __init__(self, client : Client):

        self.client = client

        self.webhook_name = "DONT DELETE Modulus Webhook"
    
    async def delete(self, channel : discord.TextChannel, webhook_id : int, message_id : int):

        webhook = await self.client.bot.fetch_webhook(int(webhook_id))
        message = await webhook.fetch_message(int(message_id))
        await message.delete()

        await self.client.file.webhook.db.execute("DELETE FROM messages WHERE message_id=?", [int(message_id)])



    async def get(self, channel : discord.TextChannel):
        if not await self.client.file.webhook.table_exists("messages"):
            await self.client.file.webhook.db.execute("CREATE TABLE messages(guild_id INTEGER, channel_id INTEGER, webhook_id INTEGER, message_id INTEGER, message STRING)")

        cursor = await self.client.file.webhook.db.execute("SELECT * FROM messages WHERE channel_id=?", [channel.id])
        messages = await cursor.fetchall()

        return messages
    
    async def send(self, channel : discord.TextChannel, username : str, avatar_url : str = None, content : str = None, embeds : typing.List[discord.Embed] = None):
        webhook : discord.Webhook = None
        
        for wh in await channel.webhooks():
            wh : discord.Webhook = wh 

            if wh.user.id == self.client.bot.user.id and wh.name == self.webhook_name:
                webhook = wh 
        
        if not webhook:
            webhook = await channel.create_webhook(name=self.webhook_name)
        
        msg = await webhook.send(content=content, username=username, avatar_url=avatar_url, embeds=embeds, wait=True)

        if not await self.client.file.webhook.table_exists("messages"):
            await self.client.file.webhook.db.execute("CREATE TABLE messages(guild_id INTEGER, channel_id INTEGER, webhook_id INTEGER, message_id INTEGER, message STRING)")
        
        message_raw = {
            "username":username,
            "avatar_url":avatar_url,
            "content":content,
            "embeds":[e.to_dict() for e in embeds],
            "id":msg.id,
            "sent_at":datetime.datetime.now().timestamp(),
            "edited_at":[]
        }
        
        await self.client.file.webhook.db.execute("INSERT INTO messages(guild_id, channel_id, webhook_id, message_id,  message) VALUES (?, ?, ?, ?, ?);", [channel.guild.id, channel.id, webhook.id, msg.id, json.dumps(message_raw)])


    

    


    
