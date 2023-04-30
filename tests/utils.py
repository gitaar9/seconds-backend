from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from seconds.game.models import Game
from seconds.user.models import User
from seconds.word.models import Word


class FiveWordsAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.super_user = User.objects.create_superuser(username="super_user", email=None, password="password")
        # Create some players
        self.player1 = User.objects.create_user(
            username='player1',
            email="player1@test.com",
            password="password",
            is_staff=False
        )
        self.player2 = User.objects.create_user(
            username='player2',
            email="player2@test.com",
            password="password",
            is_staff=False
        )
        self.player3 = User.objects.create_user(
            username='player3',
            email="player3@test.com",
            password="password",
            is_staff=False
        )
        self.player4 = User.objects.create_user(
            username='player4',
            email="player4@test.com",
            password="password",
            is_staff=False
        )
        self.players = [self.player1, self.player2, self.player3, self.player4]
        # Make sure there is some words in the db
        fake_words = [
            (1, 'hoi', 'me'),
            (1, 'doei', 'me'),
            (1, 'dag', 'me'),
            (2, 'waar', 'me'),
            (2, 'ben', 'me'),
            (2, 'ik', 'me'),
            (3, 'nu', 'me'),
            (3, 'weer', 'me'),
            (1, 'en', 'me'),
            (1, 'nog', 'me'),
            (1, 'een', 'me'),
            (2, 'setje', 'me'),
            (2, 'nieuwe', 'me'),
            (2, 'mooie', 'me'),
            (3, 'korte', 'me'),
            (3, 'worden', 'me'),

        ]
        for difficulty, word, created_by in fake_words:
            Word.objects.create(word=word, difficulty=difficulty, language='NL', added_by=created_by)
            Word.objects.create(word=word, difficulty=difficulty, language='UK', added_by=created_by)

    @staticmethod
    def get_game(code):
        return Game.objects.get(code=code)

    @staticmethod
    def get_my_team(game_json):
        teams = game_json['teams']
        for team in teams:
            if any(player['is_me'] for player in team['players']):
                return team
        return None

    def get_game_json(self):
        url = reverse('game-list')
        response = self.client.get(url, {}, format='json')
        return response.data

    @staticmethod
    def get_current_playing_team(game_json):
        for team in game_json['teams']:
            if team['currently_playing']:
                return team
        return None

    @staticmethod
    def get_current_player(game_json):
        currently_playing_team = FiveWordsAPITestCase.get_current_playing_team(game_json)
        if currently_playing_team is None:
            return None
        for player in currently_playing_team['players']:
            if player['currently_playing']:
                return User.objects.get(username=player['username'])
        return None

    def create_two_player_game(self):
        # Start a game as player 1
        self.client.force_authenticate(self.player1)
        url = reverse('game-list')
        response = self.client.post(url, {}, format='json')
        game = self.get_game(response.data['code'])
        # Join as player two
        self.client.force_authenticate(self.player2)
        url = reverse('game-join-game')
        response = self.client.post(url, {'code': game.code}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        # Start game as player two
        url = reverse('game-start')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        return self.get_game_json()
