import json

from django.urls import reverse
from rest_framework import status

from tests.utils import FiveWordsAPITestCase


class WordsTests(FiveWordsAPITestCase):
    def read_card(self):
        # Authenticate as current player
        current_player = self.get_current_player(self.get_game_json())
        self.client.force_authenticate(current_player)
        # Read first card
        url = reverse('game-start-reading-card')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        url = reverse('game-complete-turn')
        response = self.client.post(url, {"score": 4}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        return json.loads(current_player.playerinfo.current_card)['words']

    def test_get_last_10_words(self):
        self.create_two_player_game()

        # Get the words
        first_10_words = self.read_card()
        first_10_words.extend(self.read_card())

        # Normal player cant see this
        url = reverse('word-get-ten-last-used')
        print(url)
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        self.client.force_authenticate(self.super_user)
        url = reverse('word-get-ten-last-used')
        response = self.client.get(url, {}, format='json')

        self.assertEqual(set(first_10_words), {word['word'] for word in response.data})

        # Retrieve another card
        self.client.force_authenticate(self.player1)
        first_10_words = first_10_words[5:]
        first_10_words.extend(self.read_card())

        self.client.force_authenticate(self.super_user)
        url = reverse('word-get-ten-last-used')
        response = self.client.get(url, {}, format='json')

        self.assertEqual(set(first_10_words), {word['word'] for word in response.data})

