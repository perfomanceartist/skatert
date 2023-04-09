from music.models import Artist, Album, Track
import music.lastfm_api


def prepareArtist(artistName):
    if Artist.objects.filter(name=artistName).exists():
        artist = Artist.objects.get(name=artistName)
        artist.rating += 1
        return artist

    try:
        artistInfo = music.lastfm_api.artistGetInfo(artistName)
        image_small = artistInfo["artist"]["image"][0]["#text"]
        image_medium = artistInfo["artist"]["image"][1]["#text"]
        image_large = artistInfo["artist"]["image"][2]["#text"]

        new_artist = Artist(
            name=artistName,
            img_small=image_small,
            img_medium=image_medium,
            img_large=image_large
        )
        new_artist.save()
        return new_artist
    except KeyError:
        raise RuntimeError("Failed to create an artist.")


def prepareAlbum(albumInfo):
    if Album.objects.filter(name=albumInfo["title"], artist=prepareArtist(albumInfo["artist"])).exists():
        album = Album.objects.get(name=albumInfo["title"], artist=prepareArtist(albumInfo["artist"]))
        album.rating += 1
        return album

    try:
        album = Album(
            name=albumInfo["title"],
            artist=prepareArtist(albumInfo["artist"]),
            img_small=albumInfo["image"][0]["#text"],
            img_medium=albumInfo["image"][1]["#text"],
            img_large=albumInfo["image"][2]["#text"]
        )
        album.save()
        return album
    except KeyError:
        raise RuntimeError("Failed to create album.")


def prepareTrack(trackInfo):
    try:
        name = trackInfo["name"]
        artist_name = trackInfo["artist"]["name"]

        if Artist.objects.filter(name=artist_name).exists():
            artist = Artist.objects.get(name=artist_name)
            if Track.objects.filter(name=name, artist=artist).exists():
                return Track.objects.get(name=name, artist=artist)
        else:
            artist = prepareArtist(artist_name)

        extendedTrackInfo = music.lastfm_api.trackGetInfo(name, artist_name)["track"]
        if "album" in extendedTrackInfo and extendedTrackInfo["album"]:
            track = Track(name=name, album=prepareAlbum(extendedTrackInfo["album"]), artist=artist)
        else:
            track = Track(name=name, artist=artist)

        track.save()
        return track
    except KeyError:
        raise RuntimeError("Failed to prepare the track.")


def prepareUserTracks(user):
    try:
        usersTrack = music.lastfm_api.userGetLovedTracks(user)["lovedtracks"]
        if usersTrack["@attr"]["user"].lower() != user.lower():
            raise RuntimeError("Received tracks for different users: " + user + ", " + usersTrack["@attr"]["user"] + '.')

        trackList = []
        for trackInfo in usersTrack["track"]:
            trackList.append(prepareTrack(trackInfo))
        return trackList
    except KeyError:
        raise RuntimeError("Failed to prepare user's loved track.")





