from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from seconds.word.models import Word, OptionalWord
from seconds.word.serializers import WordSerializer, OptionalWordSerializer, OneWordSerializer


class WordViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, )
    queryset = Word.objects.all()
    serializer_class = WordSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.add_to_backup_file()

        # Remove from optional words
        qs = OptionalWord.objects.filter(word=instance.word)
        if qs.exists():
            qs.delete()

    @action(detail=False, methods=['post'])
    def delete_by_string(self, request, *args, **kwargs):
        serializer = OneWordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Word.objects.filter(word=serializer.validated_data['word']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def statistics(self, request, *args, **kwargs):
        qs = Word.objects.all()
        statistics_dict = {
            'total_words_count': qs.count(),
            'easy_words_count': qs.filter(difficulty=1).count(),
            'medium_words_count': qs.filter(difficulty=2).count(),
            'hard_words_count': qs.filter(difficulty=3).count(),
            'words_added_by_you': qs.filter(added_by=request.user.username).count(),
            'optional_words_count': OptionalWord.objects.count()
        }
        return Response(statistics_dict, status=status.HTTP_200_OK)


class OptionalWordViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser, )
    queryset = OptionalWord.objects.all()
    serializer_class = OptionalWordSerializer

    @action(detail=False, methods=['get'])
    def get_one(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        instance = queryset.first()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def skip_one(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset.first().delete()
        return Response(status=status.HTTP_200_OK)
