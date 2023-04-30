from django.test import TestCase
from users.models import *
from backend.lastfm_integration import loadUserLastFM
from backend.display import showUsersFavouriteTracks, showUsers, showMusicDatabase, showMusicPreferences

class UserTestCase(TestCase):

    def test_createUsersAndMakeRecommendations(self):
        users = [("Borya", "valtopech")]#, ("Seva", "DreadlyMonk"), ("Roma", "fuffilduffil"), ("Sasha", "ogz04265")]
        for (nickname, lastfmNickname) in users:
            user = loadUserLastFM(nickname, lastfmNickname)
        showUsers()
        showMusicDatabase()
        showMusicPreferences()


