
from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 
import datetime

from modules.tracking import data
from modules.tracking import spotify

def generate_time(time : datetime.timedelta):
    timeSeconds = time.total_seconds()
    day = timeSeconds // (24 * 3600)
    timeSeconds = timeSeconds % (24 * 3600)
    hour = timeSeconds // 3600
    timeSeconds %= 3600
    minutes = timeSeconds // 60
    timeSeconds %= 60
    seconds = timeSeconds

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

class Activity():
    def __init__(self, user, name : str, data : dict):

        self.user = user 
        self.name = name 

        self.time : Time = Time(user, data["total"], data["last"])
    

class Types():

    def __init__(self):
        self.online : Time = None 
        self.idle : Time= None 
        self.dnd : Time = None 
        self.offline : Time = None

class Platforms:
    desktop : Time = None 
    mobile : Time= None 
    web : Time = None 


class Voice():
    def __init__(self, user, guild_id : str, channel_id : str, time : dict):
        self.user = user 

        self.guild_id = guild_id
        self.channel_id = channel_id

        self.time = Time(user, time["total"], time["last"])

class ParsedUser():
    def __init__(self, guild, user : data.User):
        self.guild = guild 
    
        self.user = user 

        self.types : Types = Types()
        self.platforms : Platforms = Platforms
        self.activities : typing.List[Activity] = []
        self.artists : typing.List[spotify.Artist] = []
        self.tracks : typing.List[spotify.Track] = []
        self.voice_channels : typing.List[Voice] = []

        self._parse_types()
        self._parse_activities()
        self._parse_platforms()
        self._parse_spotify()
        self._parse_voice()
    
    def _parse_activities(self):

        for a_name, a_data in self.user.activities.items():
            self.activities.append(Activity(self, a_name, a_data))
        
        self.activities = list(sorted(self.activities, key=lambda item: item.time.total_time, reverse=True))
    
    def _parse_platforms(self):

        for p in ["desktop", "mobile", "web"]:
            setattr(
                self.platforms, 
                p, 
                Time(
                    self,
                    self.user.platforms[p]["total"] if p in self.user.platforms else 0,
                    self.user.platforms[p]["last"] if p in self.user.platforms else None
                )
            )
    
    def _parse_types(self):

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
        
    
    def _parse_spotify(self):

        for a in self.user.spotify:
            artist = spotify.Artist(a, self.user.spotify[a])

            self.artists.append(artist)

            for track in artist.tracks:
                track : spotify.Track = track

                if track.id not in [t.id for t in self.tracks]:
                    self.tracks.append(track)
        
        self.artists = list(sorted(self.artists, key=lambda item: item.total_listened, reverse=True))
        self.tracks = list(sorted(self.tracks, key=lambda item: item.total_listened, reverse=True))
    
    def _parse_voice(self):
        
        for guild_id, guild_channels in self.user.voice.items():

            for channel_id, duration in guild_channels.items():

                self.voice_channels.append(Voice(self, guild_id, channel_id, duration))
    
    def get_guild_voice_channels(self, guild : discord.Guild):

        value : typing.List[Voice] = []

        for channel in self.voice_channels:
            if channel.guild_id == str(guild.id):
                value.append(channel)
        
        return value

    
    def total_tracked(self):
        return self.types.online.total_time + self.types.dnd.total_time + self.types.idle.total_time + self.types.offline.total_time
    


class Guild():
    def __init__(self, client : Client, table : str):
        self.client = client 
        self.table = table
    
    async def get_user(self, user_id : int) -> ParsedUser:

        user = await self.client.data.module_tracking.get_user(self.table, user_id)

        return ParsedUser(self, user)
    
    async def total_online(self, members : typing.List[discord.Member]) -> datetime.timedelta:

        total = datetime.timedelta()

        for member in members:
            user = await self.get_user(member.id)

            total += user.types.online.total_time + user.types.dnd.total_time
        
        return total
    
    async def users_from_members(self, members : typing.List[discord.Member]) -> typing.List[ParsedUser]:
        
        users_list : typing.List[ParsedUser] = []
        for member in members:
            if member.bot:
                continue 

            users_list.append(await self.get_user(member.id))

        return users_list
            
        

        
