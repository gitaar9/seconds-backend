from random import randint

from django.db import models
from django.db.models.aggregates import Count
from django.utils import timezone


class WordQuerySet(models.QuerySet):
    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class Word(models.Model):
    DUTCH = 'NL'
    ENGLISH = 'UK'
    LANGUAGES = [
        (DUTCH, 'Dutch'),
        (ENGLISH, 'English')
    ]
    word = models.CharField(max_length=32, unique=True)
    added_by = models.CharField(max_length=50, default='Thijs')
    difficulty = models.IntegerField(default=1)
    language = models.CharField(max_length=2, choices=LANGUAGES, default=DUTCH)
    last_used = models.DateTimeField(default=timezone.now)

    objects = WordQuerySet.as_manager()

    @classmethod
    def load_words(cls):
        with open('seconds/word/backup.txt', 'rb') as f:
            for difficulty, word, created_by in map(lambda l: l.split(';'), f.read().decode('latin8').split('\n')):
                w = cls.objects.create(word=word, difficulty=int(difficulty), language=Word.DUTCH, added_by=created_by)
                print(w)

    @classmethod
    def backup_words(cls):
        with open('seconds/word/new_backup', 'w') as f:
            lines = ["{};{};{};{}\n".format(w.difficulty, w.word, w.added_by, w.language) for w in Word.objects.all()]
            f.writelines(lines)

    @classmethod
    def get_card_as_json(cls):
        all_words = Word.objects.all().order_by('last_used')
        words_array = []
        used_word_ids = []

        # Easy word
        word = all_words.filter(difficulty=1).first()
        words_array.append(word.word)
        used_word_ids.append(word.pk)

        # Medium words
        words = all_words.filter(difficulty=2)[:3]
        words_array.extend([w.word for w in words])
        used_word_ids.extend([w.pk for w in words])

        # Hard word
        word = all_words.filter(difficulty=3).first()
        words_array.append(word.word)
        used_word_ids.append(word.pk)

        # Update the last used of the words picked
        Word.objects.filter(pk__in=used_word_ids).update(last_used=timezone.now())

        return {
            "words": words_array
        }

    def add_to_backup_file(self):
        with open('seconds/word/new_backup', 'a') as f:
            f.write("{};{};{};{}\n".format(self.difficulty, self.word, self.added_by, self.language))

    def __str__(self):
        return self.word


class OptionalWord(models.Model):
    word = models.CharField(max_length=32, unique=True)

    @classmethod
    def load_optional_words(cls):
        total_words_added = 0
        with open('seconds/word/optionalBackup.txt', 'rb') as f:
            try:
                for word, _ in map(lambda l: l.split(';'), f.read().decode('latin8').split('\n')):
                    if (not Word.objects.filter(word=word).exists()) and (not OptionalWord.objects.filter(word=word).exists()):
                        w = cls.objects.create(word=word)
                        print(w)
                        total_words_added += 1
            except ValueError:
                pass
        print("Added a total of {} words".format(total_words_added))

    def __str__(self):
        return self.word
