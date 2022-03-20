

from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import datetime
import json

class User():
    def __init__(self, client : Client, user_id : int, table : str, data : tuple):

        self.client = client 
        self.data = data
        self.table = table
        
        self.user_id = user_id

        self.activities = json.loads(data[1]) if data else {}
        self.types = json.loads(data[2]) if data else {}
        self.platforms = json.loads(data[3]) if data else {}
        self.spotify = json.loads(data[4]) if data else {}
        self.messages = json.loads(data[5]) if data else {}
        self.voice = json.loads(data[6]) if data else {}
    
    async def add_type(self, name : str):
        
        if name not in self.types:
            self.types[name] = {"total":0}
            
        self.types[name]["total"] += self.client.loop_seconds
        self.types[name]["last"] = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
    
    async def save(self):

        if await self.client.file.tracking.row_exists_with_value("all_time", "user_id", self.user_id):
            await self.client.file.tracking.db.execute(
                "UPDATE all_time SET activities=?, types=?, platforms=?, spotify=?, messages=?, voice=? WHERE user_id=?", 
                [
                    json.dumps(self.activities),
                    json.dumps(self.types),
                    json.dumps(self.platforms),
                    json.dumps(self.spotify),
                    json.dumps(self.messages),
                    json.dumps(self.voice),
                    self.user_id
                ]
            )
        else:
            await self.client.file.tracking.db.execute(
                f"INSERT INTO {self.table}(user_id, activities, types, platforms, spotify, messages, voice) VALUES (?, ?, ?, ?, ?, ?, ?);", 
                [
                    self.user_id,
                    json.dumps(self.activities),
                    json.dumps(self.types),
                    json.dumps(self.platforms),
                    json.dumps(self.spotify),
                    json.dumps(self.messages),
                    json.dumps(self.voice),
                ]
            )


class DataModule():
    def __init__(self, client : Client):

        self.client = client
    
    async def check_create_table(self, name : str):

        # user_id : 000000000000000000
        # activities : {"activity_name":{"duration":0, "last_seen":"DateTime"}, ...}
        # types : {"online":{"duration":0, "last_seen":"DateTime"}, ...}
        # platforms : {"desktop":{"duration":0, "last_seen":"DateTime"}, ...}
        # spotify : {"track_id":duration:0}
        # messages : {"guild_id":{"channel_id":0, ...}, ...}
        # voice : {"channel_id":{"duration":0, "last_seen":"DateTime"}, ...}

        if not await self.client.file.tracking.table_exists(name):
            await self.client.file.tracking.db.execute(f"CREATE TABLE {name}(user_id INTEGER, activities STRING, types STRING, platforms STRING, spotify STRING, messages STRING, voice STRING)")
    
    async def get_user(self, table : str, user_id : int) -> User:

        await self.check_create_table(table)

        cursor = await self.client.file.tracking.db.execute(f"SELECT * FROM {table} WHERE user_id=?", [user_id])
        data = await cursor.fetchone()

        return User(self.client, user_id, table, data)
    


    
