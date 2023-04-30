from users.models import MusicPreferences

lastFmApiKey = "d1b2e56deb7da7dca45049f36c0c6b34"

GenreNames = ("hip hop", "rock", "rap", "pop", "alternative", "classic", "edm")


def makeOrCheckMusicPreferences():
    if len(MusicPreferences.objects.all()) != len(GenreNames):
        MusicPreferences.objects.all().delete()
        for i in range(len(GenreNames)):
            MusicPreferences(genre=i, usersBitmask=[]).save()
    return MusicPreferences.objects.all()


class GenreList:
    values = {name: False for name in GenreNames}

    def __init__(self, booleanList):
        if len(booleanList) != len(GenreNames):
            raise ValueError("Incorrect boolean input sequence.")
        for i in range(len(booleanList)):
            self.values[GenreNames[i]] = booleanList[i]
        makeOrCheckMusicPreferences()

    def setToUser(self, user):
        records = MusicPreferences.objects.all()
        for i in range(len(GenreNames)):
            records[i].usersBitmask[user.id - 1] = self.values[GenreNames[i]]
        user.save()

    def setToTrack(self, track):
        if track.genres is None:
            track.genres = [False] * len(GenreNames)

        for i in range(len(GenreNames)):
            track.genres[i] = self.values[GenreNames[i]]
        track.save()

    def unite(self, otherList):
        for name in GenreNames:
            self.values[name] = self.values[name] or otherList.values[name]

    def countMatches(self, otherList):
        count = 0
        for name in GenreNames:
            if self.values[name] == otherList.values[name]:
                count += 1
        return count

    @staticmethod
    def defaultList():
        return GenreList([False] * len(GenreNames))

    @staticmethod
    def fromTrack(track):
        return GenreList(track.genres)

    @staticmethod
    def fromUser(user):
        values = [False] * len(GenreNames)

        records = MusicPreferences.objects.all()
        for i in range(len(GenreNames)):
            values[i] = records[i].usersBitmask[user.id - 1]

        return GenreList(values)

    @staticmethod
    def fromGenreNames(genreNamesList):
        genres = GenreList.defaultList()
        for name in genreNamesList:
            if name in GenreNames:
                genres.values[name] = True
        return genres
