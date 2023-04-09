from django.test import TestCase
from users.models import *
from backend.lastfm_integration import prepareUserTracks
from backend.display import showUsersFavouriteTracks, showUsers, showMusicDatabase

class UserTestCase(TestCase):

    def test_createUsersAndMakeRecommendations(self):
        users = [("Borya", "valtopech"), ("Seva", "DreadlyMonk"), ("Roma", "fuffilduffil"), ("Sasha", "ogz04265")]
        for (nickname, lastfmNickname) in users:
            user = User(nickname=nickname, lastfm=lastfmNickname)
            user.save()
            for track in prepareUserTracks(lastfmNickname):
                user.favouriteTracks.add(track)
            user.save()
        showUsers()
        showMusicDatabase()


