from django.test import TestCase
from users.models import *
from backend.lastfm_integration import loadUserLastFM
from backend.display import showTrack, showUsers, showMusicDatabase, showMusicPreferences
from backend.backend import getRecommendations

class UserTestCase(TestCase):

    def test_createUsersAndMakeRecommendations(self):
        users = [("Borya", "valtopech"), ("Seva", "DreadlyMonk")]#, ("Roma", "fuffilduffil"), ("Sasha", "ogz04265")]
        for (nickname, lastfmNickname) in users:
            loadUserLastFM(nickname, lastfmNickname)
        showUsers()
        showMusicDatabase()
        showMusicPreferences()

        tracks = getRecommendations(User.objects.get(nickname="Borya"), 5)
        for track in tracks:
            showTrack(track)


