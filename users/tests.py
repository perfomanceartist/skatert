from django.test import TestCase

from users.models import (
    BooksPreferences,
    FilmsPreferences,
    MusicPreferences,
    Subscriptions,
    User,
    UserAuth,
)


class UserTestCase(TestCase):
    def test_create_user(self):

        userA = UserAuth.objects.create(
            nickname="testuser", passwordhash="1234", email="test@email.com"
        )

        # Создаем нового пользователя
        user = User.objects.create(
            user=userA,
            favouriteMusic=[1, 2, 3],
            favouriteFilms=[4, 5, 6],
            favouriteBooks=[7, 8, 9],
        )

        # Проверяем, что пользователь был успешно создан
        self.assertIsNotNone(user.pk)
        self.assertEqual(user.user, userA)
        self.assertListEqual(user.favouriteMusic, [1, 2, 3])
        self.assertListEqual(user.favouriteFilms, [4, 5, 6])
        self.assertListEqual(user.favouriteBooks, [7, 8, 9])


class SubscriptionsTestCase(TestCase):
    def test_create_subscription(self):
        # Создаем новую подписку
        userA = UserAuth.objects.create(
            nickname="testuser", passwordhash="1234", email="test@email.com"
        )

        # Создаем нового пользователя
        user = User.objects.create(
            user=userA,
            favouriteMusic=[1, 2, 3],
            favouriteFilms=[4, 5, 6],
            favouriteBooks=[7, 8, 9],
        )
        subscriptions = Subscriptions.objects.create(
            id=user,
            subscriptions=[2, 3, 4],
        )

        # Проверяем, что подписка была успешно создана
        self.assertIsNotNone(subscriptions.pk)
        self.assertEqual(subscriptions.id, user)
        self.assertListEqual(subscriptions.subscriptions, [2, 3, 4])


class MusicPreferencesTestCase(TestCase):
    def test_create_music_preferences(self):
        # Создаем новые музыкальные предпочтения
        music_preferences = MusicPreferences.objects.create(
            genre=1,
            usersBitmask=[True, False, True],
        )

        # Проверяем, что музыкальные предпочтения были успешно созданы
        self.assertIsNotNone(music_preferences.pk)
        self.assertEqual(music_preferences.genre, 1)
        self.assertListEqual(music_preferences.usersBitmask, [True, False, True])


class FilmsPreferencesTestCase(TestCase):
    def test_create_films_preferences(self):
        # Создаем новые кинематографические предпочтения
        films_preferences = FilmsPreferences.objects.create(
            genre=2,
            usersBitmask=[True, True, False],
        )

        # Проверяем, что кинематографические предпочтения были успешно созданы
        self.assertIsNotNone(films_preferences.pk)
        self.assertEqual(films_preferences.genre, 2)
        self.assertListEqual(films_preferences.usersBitmask, [True, True, False])


class BooksPreferencesTestCase(TestCase):
    def test_create_books_preferences(self):
        # Создаем новые литературные предпочтения
        books_preferences = BooksPreferences.objects.create(
            genre=3,
            usersBitmask=[False, True, False],
        )

        # Проверяем, что литературные предпочтения были успешно созданы
        self.assertIsNotNone(books_preferences.pk)
        self.assertEqual(books_preferences.genre, 3)
        self.assertListEqual(books_preferences.usersBitmask, [False, True, False])
