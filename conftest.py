from datetime import datetime, timedelta
import pytest

from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def news_id(news):
    return news.id,


@pytest.fixture
def comments(author, news):
    comments = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comments


@pytest.fixture
def paginator():
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(title=f'Новость {index}', text='Просто текст.',
                    date=today - timedelta(days=index))
        all_news.append(news)
    return News.objects.bulk_create(all_news)


@pytest.fixture
def more_comments(author, news):
    today = datetime.today()
    all_comment = []
    for index in range(0, 4):
        comment = Comment(news=news,
                          text=f'Просто текст. {index}',
                          created=today - timedelta(days=index),
                          author=author)
        all_comment.append(comment)
    return Comment.objects.bulk_create(all_comment)


@pytest.fixture
def comments_id(comments):
    return comments.pk,
