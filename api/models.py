from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone


class Movie(models.Model):
    data = JSONField()
    imdb_id = models.CharField(unique=True, max_length=200)

    def __str__(self):
        return 'Movie id: {}'.format(self.pk)


class Comment(models.Model):
    body = models.TextField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Comment id: {}'.format(self.pk)
