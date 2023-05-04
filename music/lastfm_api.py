import requests
from backend.parameters import lastFmApiKey


def makeGetRequest(params):
    attempts = 20
    params["api_key"] = lastFmApiKey
    url = "http://ws.audioscrobbler.com/2.0/"

    for i in range(attempts):
        try:
            response = requests.get(url, params=params, timeout=10).json()
            return response
        except (ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as error:
            print("Warning. Connection errors:", error)
    raise RuntimeError("Connection failed.")


def userGetInfo(username):
    params = {
        "method": "user.getinfo",
        "user": username,
        "format": "json"
    }
    try:
        return makeGetRequest(params)
    except (TimeoutError, requests.exceptions.JSONDecodeError) as exception:
        raise RuntimeError("Failed to get user information: " + exception)



def userGetLovedTracksAmount(username):
    params = {
        "method": "user.getLovedTracks",
        "user": username,
        "format": "json",
        "limit": 1
    }
    try:
        return int(makeGetRequest(params)["lovedtracks"]["@attr"]["total"])
    except (TimeoutError, requests.exceptions.JSONDecodeError) as exception:
        raise RuntimeError("Failed to get user's favourite tracks' amount: " + exception)


def userGetLovedTracks(username):
    params = {
        "method": "user.getLovedTracks",
        "user": username,
        "format": "json",
        "limit": 1000
    }
    try:
        return makeGetRequest(params)
    except (TimeoutError, requests.exceptions.JSONDecodeError) as exception:
        raise RuntimeError("Failed to get user's favourite tracks: " + exception)


def userGetTopTags(username, limit=10):
    params = {
        "method": "user.getTopTags",
        "user": username,
        "limit": limit,
        "format": "json"
    }
    try:
        return makeGetRequest(params)
    except (TimeoutError, requests.exceptions.JSONDecodeError) as exception:
        raise RuntimeError("Failed to get user favourite tags: " + exception)


def artistGetInfo(artistName):
    params = {
        "method": "artist.getInfo",
        "artist": "artistName",
        "format": "json",
        "autocorrect": 1
    }
    try:
        return makeGetRequest(params)
    except (TimeoutError, requests.exceptions.JSONDecodeError) as exception:
        raise RuntimeError("Failed to get artist information: " + exception)


def trackGetInfo(trackName, artistName):
    params = {
        "method": "track.getInfo",
        "track": trackName,
        "artist": artistName,
        "format": "json",
        "autocorrect": 1
    }
    try:
        return makeGetRequest(params)
    except (TimeoutError, requests.exceptions.JSONDecodeError) as exception:
        raise RuntimeError("Failed to get track information: " + exception)