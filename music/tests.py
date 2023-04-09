from django.test import TestCase
from django.urls import reverse
from music.models import Artist, Album, Track
import backend.lastfm_integration
import backend.display

class UsersLovedTracks(TestCase):

    def test_prepareUsersTrack(self):
        testingUsers = ["DreadlyMonk", "valtopech", "ogz04265", "fuffilduffil"]
        for user in testingUsers:
            backend.lastfm_integration.prepareUserTracks(user)
        backend.display.showMusicDatabase()

