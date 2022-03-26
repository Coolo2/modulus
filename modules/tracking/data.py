

from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import datetime
import json

from modules.tracking import spotify

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
    
    async def add_activity(self, name : str):

        if name not in self.activities:
            self.activities[name] = {"total":0}
            
        self.activities[name]["total"] += self.client.loop_seconds
        self.activities[name]["last"] = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
    
    async def add_platform(self, name : str):

        if name not in self.platforms:
            self.platforms[name] = {"total":0}
            
        self.platforms[name]["total"] += self.client.loop_seconds
        self.platforms[name]["last"] = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
    
    async def add_spotify(self, artist : str, track : str):

        if artist not in self.spotify:
            self.spotify[artist] = {} 
        
        if track not in self.spotify[artist]:
            self.spotify[artist][track] = 0
        
        self.spotify[artist][track] += self.client.loop_seconds
    
    async def add_voice_channel(self, guild_id : int, channel_id : int):

        if str(guild_id) not in self.voice:
            self.voice[str(guild_id)] = {}
        
        if str(channel_id) not in self.voice[str(guild_id)]:
            self.voice[str(guild_id)][str(channel_id)] = {"total":0}
        
        self.voice[str(guild_id)][str(channel_id)]["total"] += self.client.loop_seconds
        self.voice[str(guild_id)][str(channel_id)]["last"] = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")

        
    
    async def save(self):

        if await self.client.file.tracking.row_exists_with_value(self.table, "user_id", self.user_id):
            await self.client.file.tracking.db.execute(
                f"UPDATE {self.table} SET activities=?, types=?, platforms=?, spotify=?, messages=?, voice=? WHERE user_id=?", 
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

timeframes = ["all_time", "month", "week", "day"]

class DataModule():
    def __init__(self, client : Client):

        self.client = client
        self.timeframes = timeframes

        self.spotify = spotify.SpotifyClient(self.client)
    
    async def check_create_table(self, name : str):

        ## user_id : 000000000000000000 DONE
        ## activities : {"activity_name":{"duration":0, "last_seen":"DateTime"}, ...}
        ## types : {"online":{"duration":0, "last_seen":"DateTime"}, ...} DONE
        ## platforms : {"desktop":{"duration":0, "last_seen":"DateTime"}, ...}
        ## spotify : {"artist_name":{"track_id":0 ...} ... }
        # messages : {"guild_id":{"channel_id":0, ...}, ...}
        ## voice : {"channel_id":{"duration":0, "last_seen":"DateTime"}, ...}

        if not await self.client.file.tracking.table_exists(name):
            await self.client.file.tracking.db.execute(f"CREATE TABLE {name}(user_id INTEGER, activities STRING, types STRING, platforms STRING, spotify STRING, messages STRING, voice STRING)")
    
    async def get_user(self, table : str, user_id : int) -> User:

        await self.check_create_table(table)

        cursor = await self.client.file.tracking.db.execute(f"SELECT * FROM {table} WHERE user_id=?", [user_id])
        data = await cursor.fetchone()

        return User(self.client, user_id, table, data)
    
    async def clear_table(self, table : str):

        await self.client.file.tracking.db.execute(f"DELETE FROM {table}")
    
    async def do_timeframes(self):
        if not await self.client.file.tracking.table_exists("data"):
            await self.client.file.tracking.db.execute("CREATE TABLE data(timeframe STRING, last_reloaded STRING)")

        dtToday = datetime.datetime.today()
        day = f"{dtToday.year}/{dtToday.month}/{dtToday.day}"

        for tf in self.timeframes:

            if not await self.client.file.tracking.row_exists_with_value("data", "timeframe", tf):
                await self.client.file.tracking.db.execute("INSERT INTO data(timeframe, last_reloaded) VALUES (?, ?);", [tf, day])

            cursor = await self.client.file.tracking.db.execute("SELECT last_reloaded FROM data WHERE timeframe=?", [tf])
            timeframe = await cursor.fetchone()

            if tf == "day" and timeframe[0] != day:
                await self.clear_table("day")

                await self.client.file.tracking.db.execute(f"UPDATE data SET last_reloaded=? WHERE timeframe=?", [day, tf])
            
            if tf == "week" and datetime.datetime.strptime(timeframe[0], "%Y/%m/%d").weekday() == 0 and timeframe[0] != day:
                await self.clear_table("week")

                await self.client.file.tracking.db.execute(f"UPDATE data SET last_reloaded=? WHERE timeframe=?", [day, tf])
            
            if tf == "month" and datetime.datetime.strptime(timeframe[0], "%Y/%m/%d").day == 1 and timeframe[0] != day:
                await self.clear_table("month")

                await self.client.file.tracking.db.execute(f"UPDATE data SET last_reloaded=? WHERE timeframe=?", [day, tf])
    


    
