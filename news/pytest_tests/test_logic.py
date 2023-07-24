from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING, BAD_WORDS
from news.models import Comment

FORM_DATA = {'text': 'Комментарий'}
OLD_COMMENT = 'Текст комментария'
COMMENT_TEXT = 'Комментарий'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id')),
    )
)
def test_anonymous_user_cant_create_comment(client, name, args):
    url = reverse(name, args=args)
    client.post(url, data=FORM_DATA)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.parametrize(
    'parametrized_client, name, args, user',
    (
        (pytest.lazy_fixture('author_client'),
         'news:detail',
         pytest.lazy_fixture('news_id'),
         pytest.lazy_fixture('author')),
    )
)
def test_user_can_create_comment(parametrized_client, name, args, user):
    url = reverse(name, args=args)
    response = parametrized_client.post(url, data=FORM_DATA)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert (comment.news.id,) == args
    assert comment.author == user


@pytest.mark.parametrize(
    'parametrized_client, name, args',
    (
        (pytest.lazy_fixture('author_client'),
         'news:detail',
         pytest.lazy_fixture('news_id')),
    )
)
def test_user_cant_use_bad_words(parametrized_client, name, args):
    url = reverse(name, args=args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = parametrized_client.post(url, data=bad_words_data)
    assertFormError(response,
                    form='form',
                    field='text',
                    errors=WARNING
                    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.parametrize(
    'parametrized_client, name, args, expected_status',
    (
        (pytest.lazy_fixture('admin_client'),
         'news:delete',
         pytest.lazy_fixture('comments_id'),
         HTTPStatus.NOT_FOUND),
    ),
)
def test_user_cant_delete_comment_of_another_user(parametrized_client,
                                                  name,
                                                  args,
                                                  expected_status):
    delete_url = reverse(name, args=args)
    response = parametrized_client.delete(delete_url)
    assert response.status_code == expected_status
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.parametrize(
    'parametrized_client,name, comment, expected_status',
    (
        (pytest.lazy_fixture('admin_client'),
         'news:edit',
         pytest.lazy_fixture('comments'),
         HTTPStatus.NOT_FOUND),
    ),
)
def test_cant_edit_comment_of_another_user(parametrized_client,
                                           name,
                                           comment,
                                           comments_id,
                                           expected_status):
    edit_url = reverse(name, args=comments_id)
    response = parametrized_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == expected_status
    comment.refresh_from_db()
    assert comment.text == OLD_COMMENT


def test_author_can_delete_comment(author_client, news_id, comments_id):
    url = reverse('news:delete', args=comments_id)
    redirect = reverse('news:detail', args=(news_id)) + '#comments'
    response = author_client.post(url)
    assertRedirects(response, redirect)
    assert Comment.objects.count() == 0


def test_author_can_edit_note(author_client,
                              author,
                              news_id,
                              comments,
                              comments_id):
    url = reverse('news:edit', args=(comments_id))
    redirect = reverse('news:detail', args=(news_id)) + '#comments'
    response = author_client.post(url, FORM_DATA)
    assertRedirects(response, redirect)
    comments.refresh_from_db()
    assert comments.text == COMMENT_TEXT
    assert comments.author == author
