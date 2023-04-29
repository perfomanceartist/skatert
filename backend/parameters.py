lastFmApiKey = "d1b2e56deb7da7dca45049f36c0c6b34"

genreNames = ("hip hop", "rock", "rap", "pop", "alternative", "classic", "edm")
genreIdx = { genreNames[i]: i for i in range(len(genreNames)) }


def genreIndexToName(idx):
    try:
        return genreNames[idx]
    except KeyError as _:
        raise RuntimeError("No such genre.")

