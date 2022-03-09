from client import client
import discord
import setup

class DataClient():
    def __init__(self, client):
        self.client = client
    
    async def get_prefix(self, guild : discord.Guild):

        if not await self.client.file.db.table_exists("prefix"):
            await self.client.file.db.db.execute("CREATE TABLE prefix(guild_id INTEGER, prefix STRING)")

        cursor = await self.client.file.db.db.execute("SELECT prefix FROM prefix WHERE guild_id=?", (guild.id,))
        prefix = await cursor.fetchone()

        return prefix[0] if prefix else setup.default_prefix
    
    async def set_prefix(self, guild : discord.Guild, new_prefix : str):

        if await self.client.file.db.row_exists_with_value("prefix", "guild_id", guild.id):
            await self.client.file.db.db.execute(f"UPDATE prefix SET prefix=? WHERE guild_id=?", [new_prefix, guild.id])
        else:
            await self.client.file.db.db.execute("INSERT INTO prefix(guild_id, prefix) VALUES (?, ?);", [guild.id, new_prefix])

        await self.client.file.db.reload()
