from rest_framework import serializers

from api.models import Comment, Movie


class MovieSerializer(serializers.ModelSerializer):
    data = serializers.JSONField()

    class Meta:
        model = Movie
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.data = validated_data.get('data', instance.data)
        instance.save()

        return instance


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class TopSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    rank = serializers.IntegerField()
