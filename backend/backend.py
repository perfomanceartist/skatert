from music.models import Artist, Album, Track
from users.models import User, MusicPreferences
import music.lastfm_api
from parameters import genreNames, genreIdx


def getRecommendations(user, amount=20):
    pass