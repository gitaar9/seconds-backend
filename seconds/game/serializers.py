import json

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from django.http import Http404
from django.utils import timezone
from rest_framework import serializers

from seconds.game.models import Game, Team, PlayerInfo


class PlayerInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    is_me = serializers.SerializerMethodField()
    time_left = serializers.SerializerMethodField()
    card = serializers.SerializerMethodField()

    class Meta:
        model = PlayerInfo
        fields = ('username', 'is_me', 'currently_playing', 'state', 'time_left', 'card')

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
        fields = ('players', 'name', 'id', 'score', 'currently_playing')

    def create(self, validated_data):
        try:
            validated_data['game'] = self.context['request'].user.playerinfo.game
            team = Team.objects.create(**validated_data)
            return team
        except ObjectDoesNotExist:
            raise Http404


class GameSerializer(serializers.ModelSerializer):
    queryset = Game.objects.prefetch_related(Prefetch('teams', queryset=Team.objects.order_by('id')))
    teams = TeamSerializer(many=True)

    class Meta:
        model = Game
        fields = ('code', 'teams', 'state')


class CodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5)


class ScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField()

    def validate_score(self, value):
        if not (0 <= value <= 5):
            raise serializers.ValidationError("The score should be between 0 and 5")
        return value