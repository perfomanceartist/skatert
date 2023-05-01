from backend.parameters import GenreNames
from music.models import Artist, Album, Track
from users.models import User, MusicPreferences


ENUMERATION_PATTERN = "[{0:2}]"
DISPLAY_TRACK_PATTERN = "{0:60}{1:25}{2:30}{3:10}{4:10}"
DISPLAY_ARTIST_PATTERN = "{0:25}{1}"
DISPLAY_ALBUM_PATTERN = "{0:60}{1:25}{2:5}"


def showTrack(track):
    album = track.album.name if track.album is not None else ""
    print(DISPLAY_TRACK_PATTERN.format(track.name, track.artist.name, album, track.lovers, track.recommended))


def showMusicTracks():
    print("{0:66}{1:25}{2:37}{3:7}{4:10}".format("Track name", "Artist", "Album", "Loves", "Recommended"))
    for i, track in enumerate(Track.objects.all()):
        print(ENUMERATION_PATTERN.format(i), end="  ")
        showTrack(track)
    print()


def showArtists():
    print("{0:28}{1}".format("Artist name", "Rating"))
    for i, artist in enumerate(Artist.objects.all()):
        print(ENUMERATION_PATTERN.format(i), "", DISPLAY_ARTIST_PATTERN.format(artist.name, artist.listeners))
    print()


def showAlbums():
    print("{0:66}{1:25}{2}".format("Album name", "Artist name", "Album rating"))
    for i, album in enumerate(Album.objects.all()):
        print(ENUMERATION_PATTERN.format(i), "", DISPLAY_ALBUM_PATTERN.format(album.name, album.artist.name, album.listeners))
    print()


def showMusicDatabase():
    showMusicTracks()
    showArtists()
    showAlbums()


def showUsersFavouriteTracks(user):
    print("User: " + user.nickname + ", lastfm nickname: " + user.lastfm)
    print("{0:66}{1:25}{2:37}{3:7}{4:10}".format("Track name", "Artist", "Album", "Loves", "Recommended"))
    for i, track in enumerate(user.favouriteTracks.all()):
        print(ENUMERATION_PATTERN.format(i), ' ', end="")
        showTrack(track)
    print()


def showUsers():
    for user in User.objects.all():
        showUsersFavouriteTracks(user)


def showMusicPreferences():
    for i in range(len(GenreNames)):
        preference = MusicPreferences.objects.get(genre=i)
        print("Genre: {0:11}".format(GenreNames[preference.genre]), end=" ")
        for value in preference.usersBitmask:
            print("{0:2}".format(value), end=", ")
        print()
