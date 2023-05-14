import json
import random

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from django.http import Http404
from django.utils import timezone
from rest_framework import serializers

from seconds.game.asset_filenames import pion_filenames_definition
from seconds.game.models import Game, Team, PlayerInfo


class PlayerInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    is_me = serializers.SerializerMethodField()
    card = serializers.SerializerMethodField()

    class Meta:
        model = PlayerInfo
        fields = ('username', 'is_me', 'currently_playing', 'state', 'card', 'start_of_turn')

    def get_is_me(self, obj):
        return self.context['request'].user == obj.user

    def get_time_left(self, obj):
        diff = timezone.now() - obj.start_of_turn
        return max(30000 - int((diff.seconds * 1000) + (diff.microseconds / 1000)), 0)

    def get_card(self, obj):
        return json.loads(obj.current_card)


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ('players', 'name', 'id', 'score', 'currently_playing', 'pion_filename')

    @staticmethod
    def generate_new_pion_filename(game):
        used_pion_filenames = game.teams.values_list('pion_filename', flat=True).all()
        possible_pion_filenames = pion_filenames_definition.copy()
        unused_filenames = [filename for filename in possible_pion_filenames if filename not in used_pion_filenames]
        return unused_filenames[0] if unused_filenames else random.choice(possible_pion_filenames)

    def create(self, validated_data):
        try:
            game = self.context['request'].user.playerinfo.game
            validated_data['game'] = game
            validated_data['pion_filename'] = self.generate_new_pion_filename(game)
            team = Team.objects.create(**validated_data)
            return team
        except ObjectDoesNotExist:
            raise Http404


class GameSerializer(serializers.ModelSerializer):
    queryset = Game.objects.prefetch_related(Prefetch('teams', queryset=Team.objects.order_by('id')))
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ('code', 'teams', 'state', 'language', 'difficulty')
        read_only_fields = ('code', 'state', 'teams')


class CodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5)


class ScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField()

    def validate_score(self, value):
        if not (0 <= value <= 5):
            raise serializers.ValidationError("The score should be between 0 and 5")
        return value