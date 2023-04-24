from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from seconds.game.asset_filenames import pion_filenames_definition
from seconds.game.models import Game, Team, PlayerInfo
from seconds.game.serializers import GameSerializer, TeamSerializer, CodeSerializer, ScoreSerializer


class GameViewSet(viewsets.GenericViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def create(self, request, *args, **kwargs):
        game = Game.objects.create()
        my_team = Team.objects.create(game=game)
        other_team = Team.objects.create(game=game)
        other_team.pion_filename = pion_filenames_definition[1]
        other_team.save()
        PlayerInfo.objects.create(team=my_team, user=request.user)

        serializer = self.get_serializer(instance=game)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_object(self):
        try:
            return self.request.user.game
        except ObjectDoesNotExist:
            raise Http404

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=(AllowAny,))
    def spectate(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {'code': self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        serializer = self.get_serializer(instance=obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def update_game(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def leave_game(self, request, *args, **kwargs):
        try:
            if request.user.in_game and request.user.game.players.count() == 1 and \
                    request.user.game.players.first().user == request.user:
                request.user.game.delete()
            request.user.playerinfo.delete()
        except ObjectDoesNotExist:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def join_game(self, request, *args, **kwargs):
        serializer = CodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.in_game:
            return Response({"error": "User is already in game"}, status=status.HTTP_400_BAD_REQUEST)

        # Get game and put the user in the smallest team
        game = get_object_or_404(Game, code=serializer.validated_data['code'])
        smallest_team, _ = sorted([(team, team.players.count()) for team in game.teams.all()], key=lambda p: p[1])[0]
        PlayerInfo.objects.create(team=smallest_team, user=request.user)

        serializer = self.get_serializer(instance=game)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def start(self, request, *args, **kwargs):
        if request.user.in_game:
            request.user.game.start_game()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User currently not in a game'}, status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def start_reading_card(self, request, *args, **kwargs):
        my_player = self.request.user.playerinfo
        if not (my_player.currently_playing and my_player.team.currently_playing):
            return Response({'error': "It's not your turn."}, status.HTTP_400_BAD_REQUEST)
        if not my_player.state == PlayerInfo.PRE_TURN:
            return Response({'error': "Your turn is already started."}, status.HTTP_400_BAD_REQUEST)
        my_player.start_reading_card()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def complete_turn(self, request, *args, **kwargs):
        serializer = ScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not (self.request.user.playerinfo.currently_playing and self.request.user.playerinfo.team.currently_playing):
            return Response({'error': "It's not your turn."}, status.HTTP_400_BAD_REQUEST)
        my_player = self.request.user.playerinfo
        if not my_player.state == PlayerInfo.READING_CARD:
            return Response({'error': "First retrieve your card."}, status.HTTP_400_BAD_REQUEST)

        self.request.user.playerinfo.team.update_score(serializer.validated_data['score'], self.request.user)
        self.request.user.game.next_turn()
        return Response(status=status.HTTP_200_OK)


class TeamViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def perform_destroy(self, instance):
        if instance.players.count() != 0:
            if instance.game.teams.count() > 1:
                other_teams = [team for team in instance.game.teams.all() if team.pk != instance.pk]
                instance.players.all().update(team=other_teams[0])
            else:
                instance.game.delete()
                return
        instance.delete()

    @action(detail=True, methods=['get'])
    def join(self, request, *args, **kwargs):
        try:
            player = request.user.playerinfo
            player.team = self.get_object()
            player.save()
            return Response(self.get_serializer(instance=player.team).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            raise Http404
