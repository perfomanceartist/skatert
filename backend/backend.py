from typing import Optional

from backend.parameters import GenreList
from music.models import Album, Artist, Track
from users.models import MusicPreferences, User
from random import shuffle

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




def sortRecommenders(currentUser : User, recommenders : list, subscriptions : list, MATCH_LIMIT : int) -> list:
    """
    Сортировка рекомендаторов по количеству совпадающих треков    
    :return: Возвращает таблицу - id, доля совпадений, количество совпадений, новые треки      
    """
    currentUserFavouriteTracks = currentUser.favouriteTracks.all()
    recommendationsTable = list() # id, % match, matches, new tracks


    for sub in subscriptions:
        recTracks = User.objects.filter(id=sub).get().favouriteTracks.all()
        if len(recTracks) == 0:
            continue
        matches = 0
        newTracks = []
        for recommenderTrack in recTracks:
            if recommenderTrack in currentUserFavouriteTracks:
                matches += 1
            else:
                newTracks.append(recommenderTrack)
        
        matchPart =  matches / len(recTracks)   

        recommendationsTable.append((sub, matchPart, matches, newTracks, 0))

    for recommender in recommenders:
        recTracks = User.objects.filter(id=recommender).get().favouriteTracks.all()
        matches = 0
        newTracks = []
        for recommenderTrack in recTracks:
            if recommenderTrack in currentUserFavouriteTracks:
                matches += 1
            else:
                newTracks.append(recommenderTrack)
        if matches < MATCH_LIMIT: # если совпадений слишком мало, не учитываем и УДАЛЯЕМ ИЗ РЕКОМЕНДАТОРОВ
            currentUser.recommenders.remove(recommender)
            continue
        matchPart =  matches / len(recTracks)   

        recommendationsTable.append((recommender, matchPart, matches, newTracks, 1))        
    
    recommendationsTable.sort(key=lambda recommender: (recommender[4], recommender[2]))
    return recommendationsTable


def getRecommendations(currentUser, RECOMMENDED_AMOUNT=20, SIMILAR_PEOPLE_COUNT=25, MATCH_LIMIT=5) -> list:
    if Track.objects.count() < RECOMMENDED_AMOUNT:
        raise ValueError("Not enough records in the database")
    if Track.objects.count() == RECOMMENDED_AMOUNT:
        return Track.objects.all()


    # Получить список пользователей со n совпадениями, n-1 совпадений, n-2 и т.д., где n - количество избранных жанров, 
    # пока количество людей не станет больше SIMILAR_PEOPLE
    recommenders = getUserRecommenders(currentUser, SIMILAR_PEOPLE_COUNT)
    
    # Добавить в список пользователей из подписок
    #for sub in currentUser.subscriptions:
        #recommenders.append(sub)

    # Отсортировали и получили кандидатов для рекомендаций
    recommendationsTable = sortRecommenders(currentUser, recommenders, currentUser.subscriptions, MATCH_LIMIT)

    recommendations = []
    unfavouriteTracks = currentUser.unfavouriteTracks.all() or []
    for recommender in recommendationsTable:
        # Перемешивает треки - для разнообразия списка рекомендаций
        shuffle(recommender[3])
        for track in recommender[3]:
            if track in currentUser.favouriteTracks.all(): # убираем известные треки
                continue
            if track in unfavouriteTracks:  # убираем дизлайкнутые треки
                continue
            if track in recommendations: # убираем дубли
                continue

            track.recommended += 1
            track.save()

            recommendations.append(track)
            if len(recommendations) >= RECOMMENDED_AMOUNT:
                return recommendations           

    # Если не набирается RECOMMENDED_AMOUNT, дополнить ранее неизвестными самыми популярными медиа.
    for track in Track.objects.all().order_by("lovers"):
        if track in currentUser.favouriteTracks.all(): # убираем известные треки
            continue
        if track in unfavouriteTracks:  # убираем дизлайкнутые треки
            continue
        if track in recommendations: # убираем дубли
            continue

        track.recommended += 1
        track.save()

        recommendations.append(track)
        if len(recommendations) >= RECOMMENDED_AMOUNT:
                return recommendations    
    


def getUserByNickname(nickname) -> Optional[User]:
    if User.objects.filter(nickname=nickname).exists():
        return User.objects.get(nickname=nickname)
    else:
        return None


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
        result_dict["cover"] = track.album.img_large

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
