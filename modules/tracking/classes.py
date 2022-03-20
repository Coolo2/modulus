
from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 
import datetime
from modules.tracking import data

def generate_time(time : datetime.timedelta):
    timeSeconds = time.total_seconds()
    day = timeSeconds // (24 * 3600);timeSeconds = timeSeconds % (24 * 3600);hour = timeSeconds // 3600;timeSeconds %= 3600;minutes = timeSeconds // 60;timeSeconds %= 60;seconds = timeSeconds

    day = f" {round(day)}d" if day != 0 else ""
    hour = f" {round(hour)}h" if hour != 0 else ""
    minutes = f" {round(minutes)}m" if minutes != 0 else ""

    if day == "" and hour == "" and minutes == "":
        return f"{round(seconds)}s"
    
    return f"{day}{hour}{minutes}".lstrip()

def ratioFunction(x, y, z):
    return f"{round(x/(x+y+z), 2)} : {round(y/(x+y+z), 2)} : {round(z/(x+y+z), 2)}"

class Time():

    class LastSeen():
        def __init__(self, user, last_seen : datetime.datetime = None):

            self.user = user

            self.time = last_seen 

            self.relative = f"<t:{round(self.time.timestamp())}:R>" if last_seen else "Never"
            self.timestamp = "Now" if last_seen and (datetime.datetime.now() - self.time).total_seconds() < (self.user.guild.client.loop_seconds + 1) else self.relative 

    def __init__(self, user, total_time : int, last_seen : str, online_time : int = None):
        self.user = user 

        self.total_time = datetime.timedelta(seconds=total_time)
        self.last_seen = self.LastSeen(user, datetime.datetime.strptime(last_seen, '%d-%b-%Y (%H:%M:%S.%f)')) if last_seen else self.LastSeen(user)
class Types:
    online : Time = None 
    idle : Time= None 
    dnd : Time = None 
    offline : Time = None

class ParsedUser():
    def __init__(self, guild, user : data.User):
        self.guild = guild 
    
        self.user = user 

        self.types : Types = Types

        self.parse_types()
    
    def parse_types(self):

        for t in ["online", "idle", "dnd", "offline"]:
            setattr(
                self.types, 
                t, 
                Time(
                    self,
                    self.user.types[t]["total"] if t in self.user.types else 0,
                    self.user.types[t]["last"] if t in self.user.types else None
                )
            )
    


class Guild():
    def __init__(self, client : Client, table : str):
        self.client = client 
        self.table = table
    
    async def get_user(self, user_id : int):

        user = await self.client.data.module_tracking.get_user(self.table, user_id)

        return ParsedUser(self, user)

        
