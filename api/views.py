from datetime import datetime

from django.db import IntegrityError
from django.db.models import Count, F, Window
from django.db.models.functions.window import DenseRank
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.client_api import ClientApi
from api.models import Comment, Movie
from api.serializers import CommentSerializer, MovieSerializer, TopSerializer


class MovieView(APIView):
    def get(self, request):
        movies = Movie.objects.all()
        movies = self.add_optional_filtering(movies, request)
        movies = self.add_optional_ordering(movies, request)

        serializer = MovieSerializer(movies, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        title = request.data.get('title')
        if not title:
            return Response({'message': 'No field title'}, status=status.HTTP_400_BAD_REQUEST)

        data = self.fetch_movie_details_by_title(title)

        try:
            movie = Movie.objects.create(data=data, imdb_id=data.get('imdbID'))
        except IntegrityError:
            return Response({'message': 'Movie exist in db.'}, status=status.HTTP_409_CONFLICT)

        serializer = MovieSerializer(movie)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        movie = get_object_or_404(Movie.objects.all(), pk=pk)
        movie.delete()

        return Response(
            {'message': 'Movie with id {} has been deleted.'.format(pk)}, status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        movie = get_object_or_404(Movie.objects.all(), pk=pk)
        data = request.data.get('data')
        serializer = MovieSerializer(instance=movie, data=data, partial=True)

        if serializer.is_valid(raise_exception=True):
            movie_saved = serializer.save()

        return Response(
            {'message': 'Movie with id {} updated successfully.'.format(movie_saved.pk)},
            status=status.HTTP_200_OK,
        )

    def add_optional_filtering(self, query_set, request):
        filter_by = request.GET.get('filter_by')
        filter = request.GET.get('filter')

        if not filter_by or not filter:
            return query_set

        return query_set.filter(data__contains={filter_by: filter})

    def add_optional_ordering(self, query_set, request):
        order_by = request.GET.get('order_by')
        order = request.GET.get('order')

        if not order_by or not order:
            return query_set

        order_direction = '-' if order == 'desc' else ''

        return query_set.order_by('{}data__{}'.format(order_direction, order_by))

    @staticmethod
    def fetch_movie_details_by_title(title):
        return ClientApi().get_data(title)


class CommentView(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        comments = self.add_optional_filtering(comments, request)
        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        movie_id = request.data.get('movie_id')
        body = request.data.get('body')
        movie = get_object_or_404(Movie.objects.all(), pk=movie_id)

        comment = Comment.objects.create(body=body, movie=movie)
        serializer = CommentSerializer(comment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def add_optional_filtering(self, query_set, request):
        movie_id = request.GET.get('movie_id')

        if not movie_id:
            return query_set

        movie = get_object_or_404(Movie.objects.all(), pk=movie_id)

        return query_set.filter(movie=movie).order_by('created_at')


class TopView(APIView):
    def get(self, request):
        try:
            date_from = self.parse_date(request.GET.get('dateFrom'))
            date_to = self.parse_date(request.GET.get('dateTo'))
        except ValueError:
            return Response({'message': 'Bad datetime format'}, status=status.HTTP_400_BAD_REQUEST)

        if self.no_date_range(date_from, date_to):
            results = self.get_movies_rank()
        elif self.valid_date_range(date_from, date_to):
            results = self.get_movies_rank_by_date(date_from, date_to)
        else:
            return Response(
                {'message': 'Invalid datetime range'}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TopSerializer(data=list(results), many=True)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_movies_rank(self):
        return (
            Comment.objects.values('movie_id')
            .annotate(total_comments=Count('id'))
            .annotate(rank=Window(expression=DenseRank(), order_by=F('total_comments').desc()))
        )

    def get_movies_rank_by_date(self, date_from, date_to):
        return (
            Comment.objects.filter(created_at__range=(date_from, date_to))
            .values('movie_id')
            .annotate(total_comments=Count('id'))
            .annotate(rank=Window(expression=DenseRank(), order_by=F('total_comments').desc()))
        )

    def parse_date(self, value):
        return datetime.fromisoformat(value) if value else None

    def no_date_range(self, date_from, date_to):
        return date_from is None and date_to is None

    def valid_date_range(self, date_from, date_to):
        return date_from and date_to and date_from <= date_to
