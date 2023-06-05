import music.lastfm_api
from backend.display import showMusicPreferences
from backend.parameters import GenreList, GenreNames
from music.models import Album, Artist, Track
from users.models import MusicPreferences, User


def prepareArtist(artistName):
    if Artist.objects.filter(name=artistName).exists():
        artist = Artist.objects.get(name=artistName)
        artist.listeners += 1
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
        album.listeners += 1
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


def prepareTrack(trackInfo) -> Track:
    try:
        name = trackInfo["name"]
        artist_name = trackInfo["artist"]["name"]

        # Get or create artist object
        if Artist.objects.filter(name=artist_name).exists():
            artist = Artist.objects.get(name=artist_name)
            if Track.objects.filter(name=name, artist=artist).exists():
                track = Track.objects.get(name=name, artist=artist)
                track.lovers += 1
                return track
        else:
            artist = prepareArtist(artist_name)

        # Get extended track info
        rawData = music.lastfm_api.trackGetInfo(name, artist_name)

        if "track" in rawData:
            extendedTrackInfo = rawData["track"]

            # Prepare track object
            if "album" in extendedTrackInfo and extendedTrackInfo.get("album"):
                track = Track(name=name, album=prepareAlbum(extendedTrackInfo["album"]), artist=artist, genres=[False] * len(GenreNames))
            else:
                track = Track(name=name, artist=artist, genres=[False] * len(GenreNames))
            track.save()

            # Prepare genres. Set contains GENRE ID's = NUMBERS
            favouriteGenresNames = list()
            for genre in extendedTrackInfo.get("toptags", {}).get("tag", []):
                if genre["name"] in GenreNames:
                    favouriteGenresNames.append(genre["name"])
            GenreList.fromGenreNames(favouriteGenresNames).setToTrack(track)
        else:
            track = Track(name=name, artist=artist, genres=[False] * len(GenreNames))
            track.save()

        return track
    except KeyError as error:
        raise RuntimeError("Failed to prepare the track: " + str(error))


def prepareUserTracks(user):
    try:
        usersTrack = music.lastfm_api.userGetLovedTracks(user)["lovedtracks"]
        if usersTrack["@attr"]["user"].lower() != user.lower():
            raise RuntimeError(f'Received tracks for different users: {user}, {usersTrack["@attr"]["user"]}.')

        trackList = []
        for trackInfo in usersTrack["track"]:
            trackList.append(prepareTrack(trackInfo))
        return trackList
    except KeyError as error:
        raise RuntimeError("Failed to prepare user's loved track: " + str(error))


def loadUserLastFM(nickname, lastfmNickname):
    if not User.objects.filter(nickname=nickname).exists():
        return False  # if no such user we cannot integrate

    user = User.objects.filter(nickname=nickname).get()
    if user.lastfm == "" or user.lastfm == "-":
        user.lastfm = lastfmNickname
        user.save()

    lastFmAmount = music.lastfm_api.userGetLovedTracksAmount(lastfmNickname)
    dbAmount = user.favouriteTracks.count
    if dbAmount == int(lastFmAmount):
        return

    print(GenreList.fromUser(user).values.values())

    userTracksToAdd = prepareUserTracks(lastfmNickname)

    if True in GenreList.fromUser(user).values.values():
        for trackToAdd in userTracksToAdd:
            user.favouriteTracks.add(trackToAdd)
        user.save()
    else:
        userGenresCounts = [0] * len(GenreNames)

        for trackToAdd in userTracksToAdd:
            user.favouriteTracks.add(trackToAdd)
            currentGenres = GenreList.fromTrack(trackToAdd).values
            for i, name in enumerate(GenreNames):
                if currentGenres[name]:
                    userGenresCounts[i] += 1
        user.save()

        chosenUserGenres = [count * len(GenreNames) >= len(userGenresCounts) for count in userGenresCounts]
        GenreList(chosenUserGenres).setToUser(user)
