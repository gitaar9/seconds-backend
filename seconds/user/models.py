from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class User(AbstractUser):
    words_explained = models.IntegerField(default=0)
    words_explained_correct = models.IntegerField(default=0)
    words_guessed = models.IntegerField(default=0)
    words_guessed_correct = models.IntegerField(default=0)

    @property
    def game(self):
        if self.in_game:
            return self.playerinfo.game
        return None

    @property
    def in_game(self):
        try:
            p = self.playerinfo
            return True
        except ObjectDoesNotExist:
            return False

    def averages(self):
        return "Explained {.2f}, guessed {.2f}".format((self.words_explained_correct / self.words_explained) * 5,
                                                       (self.words_guessed_correct / self.words_guessed) * 5)
