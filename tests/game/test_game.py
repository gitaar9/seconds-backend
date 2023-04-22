from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from seconds.game.models import Game
from seconds.user.models import User


class AccountTests(APITestCase):
    def setUp(self):
        super().setUp()
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

    @staticmethod
    def get_game(code):
        return Game.objects.get(code=code)

    def test_create_game(self):
        """
        Ensure we can create a new game.
        """
        self.client.force_authenticate(self.player1)
        url = reverse('game-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(self.get_game(response.data['code']).teams.count(), 2)
        self.assertIn(
            self.player1,
            [player_info.user for player_info in self.get_game(response.data['code']).teams.first().players.all()]
        )
        self.assertEqual(response.data['state'], 'LOB')

    def test_integration(self):
        with self.subTest('Player1 creates a game'):
            self.client.force_authenticate(self.player1)
            url = reverse('game-list')
            response = self.client.post(url, {}, format='json')
            game = self.get_game(response.data['code'])

        with self.subTest('The other players join the game'):
            for player in [self.player2, self.player3, self.player4]:
                self.client.force_authenticate(player)
                url = reverse('game-join-game')
                response = self.client.post(url, {'code': game.code}, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
            team_1, team_2 = game.teams.all()
            self.assertIn(self.player1, [player_info.user for player_info in team_1.players.all()])
            self.assertIn(self.player2, [player_info.user for player_info in team_2.players.all()])
            self.assertIn(self.player3, [player_info.user for player_info in team_1.players.all()])
            self.assertIn(self.player4, [player_info.user for player_info in team_2.players.all()])

        with self.subTest('Player 2 decides to start the game'):
            self.client.force_authenticate(self.player2)
            url = reverse('game-start')
            response = self.client.get(url, {}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
