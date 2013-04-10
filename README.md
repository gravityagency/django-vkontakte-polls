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
    >>> poll.pk
    83838453
    >>> poll.question
    А ты занимаешься спортом? (открытое голосование)
    >>> poll.votes_count
    2170
    >>> poll.owner
    <Group: Coca-Cola>
    >>> poll.created
    datetime.datetime(2013, 4, 8, 12, 59, 2)

### Получение всех ответов голосования

    >>> poll.answers.all()
    [<Answer: Да, профессионально!>, <Answer: Регулярно хожу в спортзал.>, <Answer: Бегаю в тёплое время года.>, <Answer: Играю с друзьями в футбол.>, <Answer: Нет, я просто стараюсь вести здоровый образ жизни.>, <Answer: Нет, но очень хотелось бы.>, <Answer: Свой вариант (расскажу в комментариях).>]
    >>> poll.answers.count()
    7
    >>> answer = poll.answers.all()[0]
    >>> answer.pk
    266067655L
    >>> answer.text
    Да, профессионально!
    >>> answer.votes_count
    581
    >>> answer.rate
    26.77

### Получение всех пользователей, проголосовавших за ответ

    >>> answer.fetch_voters()
    [<User: Оля Белова>, <User: Никита Панов>, <User: Валентина Кан>, '...(remaining elements truncated)...']
    >>> answer.voters.count()
    581