from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Comment, Movie


def create_movie(imdb_id):
    return Movie.objects.create(data={'title': 'Star Wars'}, imdb_id=imdb_id)


def create_comment(movie, created_at=timezone.now()):
    return Comment.objects.create(movie=movie, body='a comment', created_at=created_at)


class MoviesTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie_1 = create_movie('01abc')
        cls.movie_2 = create_movie('02xyz')
        cls.movie_3 = create_movie('03abc')

    def test_get_all_movies(self):
        # when:
        response = self.client.get(reverse('movies'))

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_movie(self):
        # when:
        response = self.client.post(reverse('movies'), {'title': 'Star Wars'}, format='json')

        # then :
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 4)

    def test_create_movie_no_title_in_data(self):
        # when:
        response = self.client.post(reverse('movies'), {'noTitle': 'No title'}, format='json')

        # then :
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Movie.objects.count(), 3)

    def test_create_movie_which_exists_in_db(self):
        # when:
        response = self.client.post(  # NOQA: F841
            reverse('movies'), {'title': 'Star Wars'}, format='json'
        )
        response_second = self.client.post(reverse('movies'), {'title': 'Star Wars'}, format='json')

        # then:
        self.assertEqual(response_second.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response_second.json(), {'message': 'Movie exist in db.'})

    def test_delete_movie_not_found(self):
        # when:
        response = self.client.delete(reverse('movie-by-id', args=[400]))

        # then:
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_movie_with_success(self):
        # when:
        response = self.client.delete(reverse('movie-by-id', args=[2]))

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'message': 'Movie with id 2 has been deleted.'})
        self.assertEqual(Movie.objects.count(), 2)

    def test_update_movie_not_found(self):
        # when:
        response = self.client.put(reverse('movie-by-id', args=[400]))

        # then:
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_movie_with_success(self):
        # when:
        response = self.client.put(
            reverse('movie-by-id', args=[2]), data={'data': {'Title': 'Moon'}}, format='json'
        )

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'message': 'Movie with id 2 updated successfully.'})

    def test_str(self):
        # when:
        movie = self.movie_1

        # then:
        self.assertEqual(movie.__str__(), 'Movie id: 2')

    def test_get_movies_filtering(self):
        # when:
        response = self.client.get(reverse('movies'), {'filter_by': 'title', 'filter': 'Star Wars'})

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0]['data']['title'], 'Star Wars')

    def test_get_movies_ordering(self):
        # when:
        response = self.client.get(reverse('movies'), {'order_by': 'title', 'order': 'asc'})

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0]['data']['title'], 'Star Wars')


class CommentTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie_4 = create_movie('01ops')
        create_comment(cls.movie_4, datetime.fromisoformat('2019-05-01 10:00:00'))

    def test_create_comment_with_success(self):
        # when:
        response = self.client.post(
            reverse('comments'),
            {'body': 'Great movie!', 'movie_id': self.movie_4.id},
            format='json',
        )

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['movie'], self.movie_4.id)
        self.assertEqual(response.json()['id'], 2)
        self.assertEqual(Comment.objects.count(), 2)

    def test_create_comment_with_wrong_movie_id(self):
        # when:
        response = self.client.post(
            reverse('comments'), {'body': 'Wrong movie!', 'movie_id': 100}, format='json'
        )

        # then:
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_all_comments_success(self):
        # when:
        response = self.client.get(reverse('comments'))

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [{'id': 1, 'body': 'a comment', 'created_at': '2019-05-01T10:00:00Z', 'movie': 1}],
        )

    def test_get_comments_by_movie_id_success(self):
        # when:
        response = self.client.get(reverse('comments'), {'movie_id': self.movie_4.id})

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [{'id': 1, 'body': 'a comment', 'created_at': '2019-05-01T10:00:00Z', 'movie': 1}],
        )

    def test_get_comments_by_movie_id_which_not_exist(self):
        # when:
        response = self.client.get(reverse('comments'), {'movie_id': 1000})

        # then:
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_str(self):
        self.assertEqual(create_comment(self.movie_4).__str__(), 'Comment id: 3')


class TopMoviesTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie_1 = create_movie('99abc')
        create_comment(cls.movie_1, datetime.fromisoformat('2000-05-01 10:00:00'))

        cls.movie_2 = create_movie('tt111')
        create_comment(cls.movie_2, datetime.fromisoformat('2000-05-01 10:00:00'))
        create_comment(cls.movie_2, datetime.fromisoformat('2000-05-01 10:00:00'))

        cls.movie_3 = create_movie('zz123')
        create_comment(cls.movie_3, datetime.fromisoformat('2000-05-01 10:00:00'))
        create_comment(cls.movie_3, datetime.fromisoformat('2000-05-01 10:00:00'))
        create_comment(cls.movie_3, datetime.fromisoformat('2000-07-01 10:00:00'))

    def test_top_movies_by_all_comments(self):
        # when:
        response = self.client.get(reverse('top-movies'))

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [
                {'movie_id': self.movie_3.id, 'total_comments': 3, 'rank': 1},
                {'movie_id': self.movie_2.id, 'total_comments': 2, 'rank': 2},
                {'movie_id': self.movie_1.id, 'total_comments': 1, 'rank': 3},
            ],
        )

    def test_top_movies_by_comments_in_date_range(self):
        # when:
        response = self.client.get(
            reverse('top-movies'),
            {'dateFrom': '2000-05-01 00:00:00', 'dateTo': '2000-05-31 23:59:59'},
        )

        # then:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [
                {'movie_id': self.movie_2.id, 'total_comments': 2, 'rank': 1},
                {'movie_id': self.movie_3.id, 'total_comments': 2, 'rank': 1},
                {'movie_id': self.movie_1.id, 'total_comments': 1, 'rank': 2},
            ],
        )

    def test_top_movies_wrong_datetime_format(self):
        # when:
        response = self.client.get(
            reverse('top-movies'), {'dateFrom': 'April', 'dateTo': '2000-05-31 23:59:59'}
        )

        # then:
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'message': 'Bad datetime format'})

    def test_top_movies_wrong_range_datetime_format(self):
        # when:
        response = self.client.get(
            reverse('top-movies'),
            {'dateFrom': '2010-01-01 00:00:00', 'dateTo': '2000-05-31 23:59:59'},
        )

        # then:
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'message': 'Invalid datetime range'})
