import json

from django.urls import reverse
from rest_framework import status

from seconds.game.models import Game
from tests.utils import FiveWordsAPITestCase


class AccountTests(FiveWordsAPITestCase):
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
            # Player 1 and 3 are in team 1
            self.assertIn(self.player1, [player_info.user for player_info in team_1.players.all()])
            self.assertIn(self.player3, [player_info.user for player_info in team_1.players.all()])
            # Player 2 and 4 are in team 2
            self.assertIn(self.player2, [player_info.user for player_info in team_2.players.all()])
            self.assertIn(self.player4, [player_info.user for player_info in team_2.players.all()])

            self.assertIsNone(self.get_current_player(self.get_game_json()))

        with self.subTest('Player 3 decides to change his teams name to team1'):
            self.client.force_authenticate(self.player3)
            my_team_json = self.get_my_team(self.get_game_json())

            url = reverse('team-detail', args=[my_team_json['id']])
            new_team1_name = 'team1'
            response = self.client.patch(url, {'name': new_team1_name}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
            self.player1.refresh_from_db()
            self.assertEqual(self.player1.playerinfo.team.name, new_team1_name)
            self.player3.refresh_from_db()
            self.assertEqual(self.player3.playerinfo.team.name, new_team1_name)

        with self.subTest('Player 2 decides to change his teams name to team2'):
            self.client.force_authenticate(self.player2)
            my_team_json = self.get_my_team(self.get_game_json())

            url = reverse('team-detail', args=[my_team_json['id']])
            new_team2_name = 'team2'
            response = self.client.patch(url, {'name': new_team2_name}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
            self.player1.refresh_from_db()
            self.assertEqual(self.player1.playerinfo.team.name, new_team1_name)
            self.player2.refresh_from_db()
            self.assertEqual(self.player2.playerinfo.team.name, new_team2_name)
            self.player3.refresh_from_db()
            self.assertEqual(self.player3.playerinfo.team.name, new_team1_name)
            self.player4.refresh_from_db()
            self.assertEqual(self.player4.playerinfo.team.name, new_team2_name)

        with self.subTest('Player 2 decides to start the game'):
            self.client.force_authenticate(self.player2)
            url = reverse('game-start')
            response = self.client.get(url, {}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
            self.assertIsNotNone(self.get_current_player(self.get_game_json()))

        with self.subTest('Current playing player completes a turn'):
            current_player = self.get_current_player(self.get_game_json())
            self.assertEqual(json.loads(current_player.playerinfo.current_card), {})
            self.client.force_authenticate(current_player)

            # Try to complete the turn without retrieving any words
            url = reverse('game-complete-turn')
            response = self.client.post(url, {"score": 5}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

            # Retrieve words
            url = reverse('game-start-reading-card')
            response = self.client.get(url, {}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
            self.assertEqual(len(json.loads(current_player.playerinfo.current_card)['words']), 5)

            # Try to complete the turn with an impossible amount of points
            url = reverse('game-complete-turn')
            response = self.client.post(url, {"score": 7}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

            # Complete the turn with 5 points
            url = reverse('game-complete-turn')
            response = self.client.post(url, {"score": 5}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        with self.subTest('Not currently playing tries to complete a turn'):
            current_player = self.get_current_player(self.get_game_json())
            not_current_player = [p for p in self.players if p != current_player][0]

            self.client.force_authenticate(not_current_player)
            url = reverse('game-start-reading-card')
            response = self.client.get(url, {}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

            url = reverse('game-complete-turn')
            response = self.client.post(url, {"score": 4}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        with self.subTest('Finish the game'):
            for turn_nr in range(10):
                current_player = self.get_current_player(self.get_game_json())
                self.client.force_authenticate(current_player)
                url = reverse('game-start-reading-card')
                response = self.client.get(url, {}, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

                # Try to complete the turn with an impossible amount of points
                url = reverse('game-complete-turn')
                response = self.client.post(url, {"score": 5}, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            game_json = self.get_game_json()
            for team in game_json['teams']:
                if team['name'] == 'team1':
                    self.assertEqual(team['score'], 30)
                else:
                    self.assertEqual(team['score'], 25)
            self.assertEqual(game_json['state'], 'END')
