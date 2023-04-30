from music.models import Artist, Album, Track
from users.models import User, MusicPreferences
from backend.parameters import GenreList


def getRecommendations(user, amount=20) -> list:
    if amount > len(Track.objects.all()):
        raise ValueError("Not enough records in the database")
    if amount == len(Track.objects.all()):
        return Track.objects.all()

    currentUserPreferences = GenreList.fromUser(user)

    # Key - amount of common genres, value - list of user ID's.
    usersWithGenreSimilarities = {i: [] for i in range(len(MusicPreferences.objects.all()) + 1)}
    for otherUser in User.objects.all():
        similarGenres = currentUserPreferences.countMatches(GenreList.fromUser(otherUser))
        usersWithGenreSimilarities[similarGenres].append(otherUser.id)

    recommendations = []
    for genreSimilarities in range(len(MusicPreferences.objects.all()), 0, -1):
        for similarUser in usersWithGenreSimilarities[genreSimilarities]:
            for track in User.objects.get(id=similarUser).favouriteTracks.all():

                track.recommended += 1
                track.save()

                recommendations.append(track)
                if len(recommendations) >= amount:
                    return recommendations
    return recommendations


def getUserByNickname(nickname) -> User | None:
    if User.objects.filter(nickname=nickname).exists():
        return User.objects.get(nickname=nickname)
    return None


def getTrackById(trackId) -> Track | None:
    if Track.objects.filter(id=trackId).exists():
        return Track.objects.get(id=trackId)
    return None
