import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

HOME_URL = reverse('news:home')


@pytest.mark.django_db
@pytest.mark.usefixtures('paginator')
def test_news_count(client):
    response = client.get(HOME_URL)
    more_news = response.context['object_list']
    news_count = more_news.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('paginator')
def test_news(client):
    response = client.get(HOME_URL)
    more_news = response.context['object_list']
    all_dates = [news.date for news in more_news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('more_comments')
def test_comment_count(client, news_id):
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    more_comments = response.context['news']
    all_dates = [comments.created
                 for comments in more_comments.comment_set.all()]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id')),
    )
)
def test_anonymous_client_has_no_form(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_auth_has_form(author_client, news_id):
    url = reverse('news:detail', args=(news_id))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
