from rest_framework import serializers

from seconds.word.models import Word, OptionalWord, OptionalEnglishWord


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ('word', 'added_by', 'difficulty', 'language')


class OptionalWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionalWord
        fields = ('word', )


class OptionalEnglishWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionalEnglishWord
        fields = ('word', )


class OneWordSerializer(serializers.Serializer):
    word = serializers.CharField()