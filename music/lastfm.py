import django
import requests
from .models import Artist, Album, Track


class LastFm():
    def __init__(self, API_KEY="d1b2e56deb7da7dca45049f36c0c6b34"):
        self.API_KEY = API_KEY
        self.url = "http://ws.audioscrobbler.com/2.0/"
    
    def check_user(self, username):
        params = {
            "method":"user.getinfo",
            "user":username,
            "api_key":self.API_KEY,
            "format":"json"
        }
        response = requests.get(self.url, params=params)
        if response.status_code != 200:
            return False
        else:
            return True
        
        json_response = response.json()
       
    def extract_artist_info(self, artist):
        name = artist["name"]

        if Artist.objects.filter(name = name).exists():
            return Artist.objects.get(name = name)
        

        
        params = {
            "method":"artist.getInfo",
            "artist":artist,
            "api_key":self.API_KEY,
            "format":"json"
        }
        response = requests.get(self.url, params=params)
        if response.status_code != 200:
            return False
        json_response = response.json()
        info = json_response["artist"]
        image_small = info["image"][0]["#text"]
        image_medium = info["image"][1]["#text"]
        image_large = info["image"][2]["#text"]

        new_artist = Artist(
            name=name,
            img_small=image_small,
            img_medium=image_medium,
            img_large=image_large
            )
        new_artist.save()
        return new_artist

    def extract_album_info(self, album):
        name = album["title"]
        artist_name = album["artist"]
        #try:
        artist = Artist.objects.get(name=artist_name)
        #except django.core.exceptions.ObjectDoesNotExist:
        if Album.objects.filter(name=name,artist=artist).exists():
            return Album.objects.get(name=name,artist=artist)
                
        image_small = album["image"][0]["#text"]
        image_medium = album["image"][1]["#text"]
        image_large = album["image"][2]["#text"]

        new_album = Album(
            name=name,
            artist=artist,
            img_small=image_small,
            img_medium=image_medium,
            img_large=image_large
        )
        new_album.save()
        return new_album

    def extract_track_info(self, track):
        print()
        print(track)
        print()
        name = track["name"]
        artist_name = track["artist"]["name"]

        if Artist.objects.filter(name=artist_name).exists():
            artist = Artist.objects.get(name=artist_name)
            if Track.objects.filter(name=name,artist=artist).exists():
                return Track.objects.get(name=name,artist=artist)
        

        
        params = {
            "method":"track.getInfo",
            "track":name,
            "artist":artist_name,
            "api_key":self.API_KEY,
            "format":"json"
        }
        response = requests.get(self.url, params=params)
        if response.status_code != 200:
            return False
        json_response = response.json()
        print(json_response)
        info = json_response["track"]
        artist = self.extract_artist_info(info["artist"])
        album = self.extract_album_info(info["album"])

        new_track = Track(
            name=name,
            album=album,
            artist=artist
        )
        new_track.save()
        return new_track

        #image_small = track["image"][0]["#text"]
        #image_medium = track["image"][1]["#text"]
        #image_large = track["image"][2]["#text"]



    def download_from_user(self, username):
        if not self.check_user(username):
            return False
        params = {
            "method":"user.getLovedTracks",
            "user":username,
            "api_key":self.API_KEY,
            "format":"json"
        }
        response = requests.get(self.url, params=params)
        if response.status_code != 200:
            return False
        
        fav_tracks = []
        json_response = response.json()
        print(json_response)
        total_pages = int(json_response["lovedtracks"]["@attr"]["totalPages"])
        for track in json_response["lovedtracks"]["track"]:
            fav_tracks.append(self.extract_track_info(track))
        
        for page in range(1, total_pages):
            params = {
                "method":"user.getinfo",
                "page":str(page),
                "user":username,
                "api_key":self.API_KEY,
                "format":"json"
            }
            response = requests.get(self.url, params=params)
            json_response = response.json()
            for track in json_response["lovedtracks"]["track"]:
                fav_tracks.append(self.extract_track_info(track))
        
        return fav_tracks



        