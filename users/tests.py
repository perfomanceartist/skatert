from django.test import TestCase

from backend.backend import getRecommendations
from backend.display import (showMusicDatabase, showMusicPreferences,
                             showTrack, showUsers)
from backend.lastfm_integration import loadUserLastFM
from users.models import *


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
