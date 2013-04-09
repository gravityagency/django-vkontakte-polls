# Django Vkontakte Polls

[![Build Status](https://travis-ci.org/ramusus/django-vkontakte-polls.png?branch=master)](https://travis-ci.org/ramusus/django-vkontakte-polls) [![Coverage Status](https://coveralls.io/repos/ramusus/django-vkontakte-polls/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-vkontakte-polls)

Приложение позволяет взаимодействовать с голосованиями групп через Вконтакте API используя стандартные модели Django

## Установка

    pip install django-vkontakte-polls

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'vkontakte_api',
        'vkontakte_groups',
        'vkontakte_users',
        'vkontakte_wall',
        'vkontakte_polls',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                         # to keep in DB expired access tokens
    OAUTH_TOKENS_VKONTAKTE_CLIENT_ID = ''                               # application ID
    OAUTH_TOKENS_VKONTAKTE_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_VKONTAKTE_SCOPE = ['ads,wall,photos,friends,stats']    # application scopes
    OAUTH_TOKENS_VKONTAKTE_USERNAME = ''                                # user login
    OAUTH_TOKENS_VKONTAKTE_PASSWORD = ''                                # user password
    OAUTH_TOKENS_VKONTAKTE_PHONE_END = ''                               # last 4 digits of user mobile phone

## Примеры использования

### Получение голосования

    >>> from vkontakte_polls.models import Poll, Group, Post
    >>> group = Group.remote.fetch(ids=[16297716])[0]
    >>> post = Post.objects.create(remote_id='-16297716_190770', wall_owner=group)
    >>> poll = Poll.remote.fetch(83838453, group, post)
    >>> poll.question