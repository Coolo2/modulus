from client import client
import discord
import setup

import time 
import datetime

import modules.tracking.data

import json

class Log():
    def __init__(self, client, data : tuple):
        self.guild_id = data[0]
        self.time = datetime.datetime.fromtimestamp(data[1])

        self.user_id = data[2]
        self.user_tag = data[3]

        self.log_type = data[4]
        self.description = data[5]

        self.timestamp_raw = data[1]
    
    def to_dict(self):
        return {
            "guild_id":str(self.guild_id), 
            "timestamp":str(self.timestamp_raw), 
            "user_id":str(self.user_id),
            "user_tag":self.user_tag,
            "log_type":self.log_type, 
            "description":self.description
        }

class DataClient():
    def __init__(self, client):
        self.client = client

        self.module_tracking = modules.tracking.data.DataModule(self.client)
    
    async def get_prefix(self, guild : discord.Guild):

        if not await self.client.file.db.table_exists("prefix"):
            await self.client.file.db.db.execute("CREATE TABLE prefix(guild_id INTEGER, prefix STRING)")

        cursor = await self.client.file.db.db.execute("SELECT prefix FROM prefix WHERE guild_id=?", (guild.id,))
        prefix = await cursor.fetchone()

        return prefix[0] if prefix else setup.default_prefix
    
    async def set_prefix(self, guild : discord.Guild, new_prefix : str):

        if not await self.client.file.db.table_exists("prefix"):
            await self.client.file.db.db.execute("CREATE TABLE prefix(guild_id INTEGER, prefix STRING)")

        if await self.client.file.db.row_exists_with_value("prefix", "guild_id", guild.id):
            await self.client.file.db.db.execute("UPDATE prefix SET prefix=? WHERE guild_id=?", [new_prefix, guild.id])
        else:
            await self.client.file.db.db.execute("INSERT INTO prefix(guild_id, prefix) VALUES (?, ?);", [guild.id, new_prefix])

        await self.client.file.db.reload()
    
    async def add_log(self, guild : discord.Guild, user : discord.User, log_type : str, description : str):

        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))

        if not await self.client.file.db.table_exists("logs"):
            await self.client.file.db.db.execute("CREATE TABLE logs(guild_id INTEGER, time INTEGER, user_id INTEGER, user STRING, type STRING, description STRING)")
        
        await self.client.file.db.db.execute("INSERT INTO logs(guild_id, time, user_id, user, type, description) VALUES (?, ?, ?, ?, ?, ?);", [guild.id, timestamp, user.id, str(user), log_type, description])
    
    async def get_logs(self, guild : discord.Guild):
        if not await self.client.file.db.table_exists("logs"):
            await self.client.file.db.db.execute("CREATE TABLE logs(guild_id INTEGER, time INTEGER, user_id INTEGER, user STRING, type STRING, description STRING)")
        
        cursor = await self.client.file.db.db.execute("SELECT * FROM logs WHERE guild_id=?", [guild.id])
        logs = await cursor.fetchall()

        all = []
        for log in logs:
            all.append(Log(self.client, log))
        
        return reversed(all)
    
    async def clear_logs(self, guild : discord.Guild):
        if not await self.client.file.db.table_exists("logs"):
            await self.client.file.db.db.execute("CREATE TABLE logs(guild_id INTEGER, time INTEGER, user_id INTEGER, user STRING, type STRING, description STRING)")
        
        cursor = await self.client.file.db.db.execute("DELETE FROM logs WHERE guild_id=?", [guild.id])
        
        return cursor
    
    async def get_modules(self, guild : discord.Guild) -> list:
        if not await self.client.file.db.table_exists("modules"):
            await self.client.file.db.db.execute("CREATE TABLE modules(guild_id INTEGER, modules STRING)")
        
        cursor = await self.client.file.db.db.execute("SELECT modules FROM modules WHERE guild_id=?", (guild.id,))
        modules = await cursor.fetchone()

        return json.loads(modules[0]) if modules else []

    async def enable_module(self, guild : discord.Guild, module_name : str):
        if not await self.client.file.db.table_exists("modules"):
            await self.client.file.db.db.execute("CREATE TABLE modules(guild_id INTEGER, modules STRING)")
        
        if await self.client.file.db.row_exists_with_value("modules", "guild_id", guild.id):

            modules = await self.get_modules(guild)

            if module_name not in modules:
                modules.append(module_name)

                await self.client.file.db.db.execute("UPDATE modules SET modules=? WHERE guild_id=?", [json.dumps(modules), guild.id])
        else:
            await self.client.file.db.db.execute("INSERT INTO modules(guild_id, modules) VALUES (?, ?);", [guild.id, json.dumps([module_name])])
    
    async def disable_module(self, guild : discord.Guild, module_name : str):
        if not await self.client.file.db.table_exists("modules"):
            await self.client.file.db.db.execute("CREATE TABLE modules(guild_id INTEGER, modules STRING)")
        
        if await self.client.file.db.row_exists_with_value("modules", "guild_id", guild.id):

            modules = await self.get_modules(guild)

            if module_name in modules:
                modules.remove(module_name)

                await self.client.file.db.db.execute("UPDATE modules SET modules=? WHERE guild_id=?", [json.dumps(modules), guild.id])
        else:
            await self.client.file.db.db.execute("INSERT INTO modules(guild_id, modules) VALUES (?, ?);", [guild.id, json.dumps([module_name])])
    
    async def module_enabled(self, guild : discord.Guild, module_name : str):

        return module_name in await self.get_modules(guild)
    


