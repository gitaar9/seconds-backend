import json
import random

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone

from seconds.user.models import User
from seconds.word.models import Word


def random_string():
    return str(random.randint(10000, 99999))


class Game(models.Model):
    LOBBY = 'LOB'
    PLAYING = 'PLA'
    ENDED = 'END'
    GAME_STATES = [
        (LOBBY, 'Lobby'),
        (PLAYING, 'Playing'),
        (ENDED, 'Ended'),
    ]
    state = models.CharField(max_length=3, choices=GAME_STATES, default=LOBBY)
    code = models.CharField(max_length=5, default=random_string)
    language = models.CharField(max_length=2, choices=Word.LANGUAGES, default=Word.DUTCH)

    @property
    def players(self):
        return PlayerInfo.objects.filter(team__game=self)

    def start_game(self):
        if self.state == self.LOBBY:
            self.teams.first().start_turn()
            self.state = self.PLAYING
            self.save()

    def next_turn(self):
        # Switch the active team
        try:
            current_team = self.teams.get(currently_playing=True)
            current_team.currently_playing = False
            current_team.save()

            next_team = self.teams.filter(pk__gt=current_team.pk).order_by('pk').first() or self.teams.order_by('pk').first()
        except ObjectDoesNotExist:
            next_team = self.teams.order_by('pk').first()
        next_team.start_turn()

    @classmethod
    def create_test_game(cls, amount_of_teams=2, amount_of_players=4):
        game = cls.objects.create()
        teams = [Team.objects.create(game=game, name="Team " + str(nr), score=random.randint(0, 10)) for nr in range(amount_of_teams)]
        users = [User.create_test_user("user" + str(nr)) for nr in range(amount_of_players)]

        # divide the players equally over the teams
        team_idx = 0
        for cnt, user in enumerate(users):
            if cnt % (amount_of_players / amount_of_teams) == 0:
                team_idx += 1
            PlayerInfo.objects.create(team=teams[team_idx - 1], user=user)

        game.start_game()
        return game

    def __str__(self):
        return ", ".join([str(t) for t in self.teams.all()])


class Team(models.Model):
    name = models.CharField(max_length=15, default="Team name")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='teams')
    currently_playing = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    class Meta:
        ordering = ['-score']

    def start_turn(self):
        # Switch the active player
        try:
            current_player = self.players.get(currently_playing=True)
            current_player.end_turn()
            next_player = self.players.filter(pk__gt=current_player.pk).order_by('pk').first() or self.players.order_by('pk').first()
        except ObjectDoesNotExist:
            next_player = self.players.order_by('pk').first()

        next_player.start_turn()
        self.currently_playing = True
        self.save()

    def update_score(self, score, player):
        self.score = self.score + score
        self.save()

        # Check whether the is won
        if self.score >= 30:
            self.game.state = Game.ENDED
            self.game.save()

        # Statistics
        # TODO later

    def __str__(self):
        return self.name + ": " + ", ".join([str(p) for p in self.players.all()])


class PlayerInfo(models.Model):
    PRE_TURN = 'PRE'
    READING_CARD = 'REA'
    AFTER_TURN = 'AFT'
    TURN_STATES = [
        (PRE_TURN, 'Before reading the card'),
        (READING_CARD, 'Reading the card'),
        (AFTER_TURN, 'After reading the card'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currently_playing = models.BooleanField(default=False)
    state = models.CharField(max_length=3, choices=TURN_STATES, default=AFTER_TURN)
    start_of_turn = models.DateTimeField(default=timezone.now)
    current_card = models.CharField(max_length=2048, default="{}")

    def start_turn(self):
        self.currently_playing = True
        self.state = self.PRE_TURN
        self.save()

    def start_reading_card(self):
        self.state = self.READING_CARD
        self.start_of_turn = timezone.now()
        self.current_card = json.dumps(Word.get_card_as_json(self.game))
        self.save()

    def end_turn(self):
        self.currently_playing = False
        self.state = self.AFTER_TURN
        self.save()

    @property
    def game(self):
        return self.team.game

    def __str__(self):
        return self.user.username
