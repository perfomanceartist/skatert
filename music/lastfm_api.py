import requests


def makeGetRequest(params):
    """ Completes parameters with our API key.
    Shouldn't it be located in the configuration? """
    params["api_key"] = "d1b2e56deb7da7dca45049f36c0c6b34"
    url = "http://ws.audioscrobbler.com/2.0/"
    # print("Using link: " + requests.get(url, params=params, timeout=3).url)
    return requests.get(url, params=params, timeout=3).json()


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


def userGetLovedTracks(username):
    params = {
        "method": "user.getLovedTracks",
        "user": username,
        "format": "json"
    }
    try:
        return makeGetRequest(params)
    except (TimeoutError, requests.exceptions.JSONDecodeError) as exception:
        raise RuntimeError("Failed to get user's favourite tracks: " + exception)


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
        # "autocorrect": 1
    }
    try:
        return makeGetRequest(params)
    except (TimeoutError, requests.exceptions.JSONDecodeError) as exception:
        raise RuntimeError("Failed to get track information: " + exception)