from music.models import Artist, Album, Track
from users.models import User, MusicPreferences


ENUMERATION_PATTERN = "[{0:2}]"
DISPLAY_TRACK_PATTERN = "{0:60}{1:25}{2:}"
DISPLAY_ARTIST_PATTERN = "{0:25}{1:25}"
DISPLAY_ALBUM_PATTERN = "{0:60}{1:25}:{2:5}"

def showTrack(track):
    album = track.album.name if track.album is not None else ""
    print(DISPLAY_TRACK_PATTERN.format(track.name, track.artist.name, album))


def showMusicTracks():
    for i, track in enumerate(Track.objects.all()):
        print(ENUMERATION_PATTERN.format(i), end=" ")
        showTrack(track)
    print()


def showArtists():
    for i, artist in enumerate(Artist.objects.all()):
        print(ENUMERATION_PATTERN.format(i), ' ', DISPLAY_ARTIST_PATTERN.format(artist.name, artist.rating))
    print()


def showAlbums():
    for i, album in enumerate(Album.objects.all()):
        print(ENUMERATION_PATTERN.format(i), ' ', DISPLAY_ALBUM_PATTERN.format(album.name, album.artist.name, album.rating))
    print()


def showMusicDatabase():
    print("Tracks:")
    showMusicTracks()
    print("Artists:")
    showArtists()
    print("Albums:")
    showAlbums()


def showUsersFavouriteTracks(user):
    print("User: " + user.nickname + ", lastfm nickname: " + user.lastfm)
    for i, track in enumerate(user.favouriteTracks.all()):
        print(ENUMERATION_PATTERN.format(i), ' ', end="")
        showTrack(track)
    print()


def showUsers():
    for user in User.objects.all():
        showUsersFavouriteTracks(user)
