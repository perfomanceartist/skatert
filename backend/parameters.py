from users.models import MusicPreferences

lastFmApiKey = "d1b2e56deb7da7dca45049f36c0c6b34"

GenreNames = ("hip hop", "rock", "rap", "pop", "alternative", "classic", "edm")


class GenreList:
    values = {name: False for name in GenreNames}

    def __init__(self, booleanList):
        if len(booleanList) != len(GenreNames):
            raise ValueError("Incorrect boolean input sequence.")
        for i in range(len(booleanList)):
            self.values[GenreNames[i]] = booleanList[i]

    def setToUser(self, user):
        for i in range(len(GenreNames)):
            record = MusicPreferences.objects.get(genre=i)
            record.usersBitmask[user.id - 1] = self.values[GenreNames[i]]
            record.save()

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

    def show(self):
        print(*self.values.values(), sep=", ")

    @staticmethod
    def defaultList():
        return GenreList([False] * len(GenreNames))

    @staticmethod
    def fromTrack(track):
        return GenreList(track.genres)

    @staticmethod
    def fromUser(user):
        tValues = [False] * len(GenreNames)
        for i in range(len(GenreNames)):
            record = MusicPreferences.objects.get(genre=i)
            tValues[i] = record.usersBitmask[user.id - 1]

        return GenreList(tValues)

    @staticmethod
    def fromGenreNames(genreNamesList):
        genres = GenreList.defaultList()
        for name in genreNamesList:
            if name in GenreNames:
                genres.values[name] = True
        return genres
