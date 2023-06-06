from typing import Optional

from backend.parameters import GenreList
from music.models import Album, Artist, Track
from users.models import MusicPreferences, User


def getUserRecommenders(currentUser : User, SIMILAR_PEOPLE_COUNT : int) -> list:
    if len(currentUser.recommenders) >= SIMILAR_PEOPLE_COUNT:
        return currentUser.recommenders

    currentUserPreferences = GenreList.fromUser(currentUser)
    # Проходит по всем пользователям, формируя массив списков usersWithGenreSimilarities.
    # Индекс массива - количество совпадений по жанрам, значение массива - список пользователей с таким числом совпадений.
    usersWithGenreSimilarities = {i: [] for i in range(len(MusicPreferences.objects.all()) + 1)}
    for otherUser in User.objects.all():
        similarGenres = currentUserPreferences.countMatches(GenreList.fromUser(otherUser))
        usersWithGenreSimilarities[similarGenres].append(otherUser.id)

    # Считаем с конца
    for genreSimilarities in range(len(MusicPreferences.objects.all()), 0, -1):
         for similarUser in usersWithGenreSimilarities[genreSimilarities]:
            if similarUser not in currentUser.recommenders:
                currentUser.recommenders.append(similarUser)
                if len(currentUser.recommenders) >= SIMILAR_PEOPLE_COUNT:
                    break

    
    currentUser.save()
    return currentUser.recommenders


def getRecommendations(currentUser, SIMILAR_PEOPLE_COUNT=25, MATCH_LIMIT=0.6, RECOMMENDED_AMOUNT=20) -> list:
    if Track.objects.count() < RECOMMENDED_AMOUNT:
        raise ValueError("Not enough records in the database")
    if Track.objects.count() == RECOMMENDED_AMOUNT:
        return Track.objects.all()



    recommenders = getUserRecommenders(currentUser, SIMILAR_PEOPLE_COUNT)
    

    recommendations = []
    unfavouriteTracks = currentUser.unfavouriteTracks.all() or []
    for recommender in recommenders:
        for track in User.objects.get(id=recommender).favouriteTracks.order_by('recommended'):
            if track in currentUser.favouriteTracks.all():
                continue
            if track in unfavouriteTracks:  # skip unfavourite tracks
                continue

            track.recommended += 1
            track.save()

            recommendations.append(track)
            if len(recommendations) >= RECOMMENDED_AMOUNT:
                return recommendations

    

    if len(recommendations) >= RECOMMENDED_AMOUNT:
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
