from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import datetime 
import requests 
import os

base = 'https://api.spotify.com/v1/'
auth = 'https://accounts.spotify.com/api/token'

class SpotifyAuth():

    def __init__(self, id, secret):

        self.id = id 
        self.secret = secret
    
    def login(self):

        auth_response = requests.post(auth, {
            'grant_type': 'client_credentials',
            'client_id': self.id,
            'client_secret': self.secret,
        })

        auth_response_data = auth_response.json()
        self.token = auth_response_data['access_token']

class Artist():
    def __init__(self, name : str, tracks : dict, data : dict = None):
        self.name = name 
        self.tracks = []

        self.total_listened = datetime.timedelta()

        for track in tracks:

            total_listened = datetime.timedelta(seconds=tracks[track])
            self.tracks.append(Track(self, track, total_listened))
            self.total_listened += total_listened
        
        self.url : str = None 

        if data:
            self.url = data["external_urls"]["spotify"]

class Album():
    def __init__(self, data : dict):
        self.type = data["album_type"]
        self.url = data["external_urls"]["spotify"]
        self.name = data["name"]
        self.total_tracks = data["total_tracks"]

class TrackAudioFeatures():

    def __init__(self, features):
        self.supportedTypes = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
        self.danceability : int = None 
        self.energy : int = None 
        self.speechiness : int = None 
        self.acousticness : int = None 
        self.instrumentalness : int = None 
        self.liveness : int = None 
        self.valuence : int = None 
        self.tempo : int = None

        for feature in features:
            if feature in self.supportedTypes:
                setattr(self, feature, features[feature])
        
        self.supportedTypes = sorted(self.supportedTypes, key=lambda item: getattr(self, item), reverse=True)

class Track():
    def __init__(self, artist : Artist, id : str, total_listened : datetime.timedelta):
        self.artist = artist
        self.id = id
        self.total_listened = total_listened

        self.name : str = None 
        self.url : str = None 
        self.popularity : int = None 
        self.album : Album = None
        self.artists : typing.List[Artist] = []
        self.duration : int = None

        self.features : TrackAudioFeatures = None

    def add_details(self, details : dict):
        
        self.name = details["name"]
        self.url = details["external_urls"]["spotify"]
        self.popularity = details["popularity"]
        self.album = Album(details["album"])
        self.duration = details["duration_ms"]

        for artist in details["artists"]:
            self.artists.append(Artist(artist["name"], [], artist))
        
    def add_features(self, features : dict):
        supportedTypes = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
        result = {}

        for feature in features:
            if feature in supportedTypes:
                result[feature] = features[feature]
        
        self.features = TrackAudioFeatures(result)

class SpotifyClient():
    def __init__(self, client : Client):
        self.client = client

        self.auth = SpotifyAuth(os.getenv("spotifyId"), os.getenv("spotifySecret"))
        self.auth.login()

        self.headers = {
            'Authorization': f'Bearer {self.auth.token}'
        }

        self.getTrackDetailMax = 50
        self.getTrackFeatureMax = 100
        self.getMultipleArtistMax = 50
    
    async def get_track_details(self, tracks : typing.List[Track]):

        tracks = tracks[:self.getTrackDetailMax]

        data = await self.client.http.json_request("GET", url=base + f"tracks?ids={','.join([track.id for track in tracks])}", headers=self.headers)

        if "tracks" in data:

            for track in tracks:
                for td in data["tracks"]:
                    if track.id == td["id"]:
                        track.add_details(td)
        
        return tracks
    
    async def get_track_features(self, tracks : typing.List[Track]):

        tracks = tracks[:self.getTrackFeatureMax]

        data = await self.client.http.json_request("GET", url=base + f"audio-features?ids={','.join([track.id for track in tracks])}", headers=self.headers)

        if "audio_features" in data:

            for track in tracks:
                for td in data["audio_features"]:
                    if track.id == td["id"]:
                        track.add_features(td)
        
        return tracks

        
        
