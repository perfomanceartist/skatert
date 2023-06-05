from typing import Optional

from backend.parameters import GenreList
from music.models import Album, Artist, Track
from users.models import MusicPreferences, User


def getRecommendations(currentUser, amount=20) -> list:
    if amount > len(Track.objects.all()):
        raise ValueError("Not enough records in the database")
    if amount == len(Track.objects.all()):
        return Track.objects.all()

    currentUserPreferences = GenreList.fromUser(currentUser)

    recommendations = []
    unfavouriteTracks = currentUser.unfavouriteTracks.all() or []
    for recommender in currentUser.recommenders:
        for track in User.objects.get(id=recommender).favouriteTracks.order_by('recommended'):
            if track in currentUser.favouriteTracks.all():
                continue
            if track in unfavouriteTracks:  # skip unfavourite tracks
                continue

            track.recommended += 1
            track.save()

            recommendations.append(track)
            if len(recommendations) >= amount:
                return recommendations

    # Key - amount of common genres, value - list of user ID's.
    usersWithGenreSimilarities = {i: [] for i in range(len(MusicPreferences.objects.all()) + 1)}
    for otherUser in User.objects.all():
        similarGenres = currentUserPreferences.countMatches(GenreList.fromUser(otherUser))
        usersWithGenreSimilarities[similarGenres].append(otherUser.id)

    for genreSimilarities in range(len(MusicPreferences.objects.all()), 0, -1):
        for similarUser in usersWithGenreSimilarities[genreSimilarities]:
            for track in User.objects.get(id=similarUser).favouriteTracks.order_by('recommended'):
                # Skips common tracks.
                if track in currentUser.favouriteTracks.all():
                    continue

                track.recommended += 1
                track.save()

                if similarUser not in currentUser.recommenders:
                    currentUser.recommenders.append(similarUser)
                    currentUser.save()

                recommendations.append(track)
                if len(recommendations) >= amount:
                    return recommendations

    if len(recommendations) >= amount:
        return recommendations
    raise ValueError("Not enough records in the database")


def getUserByNickname(nickname) -> Optional[User]:
    return User.objects.get(nickname=nickname)


def getArtistByName(artist: str) -> Optional[Artist]:
    return Artist.objects.get(name=artist)


def getAlbumByName(album: str) -> Optional[Artist]:
    return Album.objects.get(name=album)


def getTrackById(trackId: int) -> Optional[Track]:
    return Track.objects.get(id=trackId)


def getTrackIdByInfo(name_str: str, artist_str: str, album_str: str=None) -> Optional[int]:
    if not name_str:
        return None

    if (artist := getArtistByName(artist_str)) is None:
        return None

    if album_str and (album := getAlbumByName(album_str)) is not None:
        if Track.objects.filter(name=name_str, artist=artist, album=album).exists():
            return Track.objects.get(name=name_str, artist=artist, album=album).id

    if Track.objects.filter(name=name_str, artist=artist).exists():
        return Track.objects.get(name=name_str, artist=artist).id


def getTrackByInfo(name_str: str, artist_str: str, album_str: str=None) -> Optional[Track]:
    if (trackId := getTrackIdByInfo(name_str, artist_str, album_str)) is not None:
        return getTrackById(trackId)


def getTrackInformation(track) -> dict:
    result_dict = {
        "name": track.name,
        "artist": track.artist.name,
        "genres": track.genres,
        "listeners": track.lovers,
        "recommended": track.recommended
    }

    if track.album:
        result_dict["album"] = track.album.name

    return result_dict


def prepareUserInfo(user) -> dict:
    return {
        "nickname": user.nickname,
        "lastFmNickname": user.lastfm,
        "favouriteTracksAmount": len(user.favouriteTracks.all()),
        "genres": dict(GenreList.fromUser(user).values),
        "recommenders": list(user.recommenders)
    }


def tryRemoveDislike(user: User, track: Track):
    "If dislike is set, remove it."
    if track in (user.unfavouriteTracks.all() or []):
        user.unfavouriteTracks.remove(track)
        user.save()


def tryRemoveLike(user: User, track: Track):
    "If like is set, remove it."
    if track in (user.favouriteTracks.all() or []):
        user.favouriteTracks.remove(track)
        user.save()
