from vkontakte_users.factories import UserFactory
from models import Poll, Answer
from datetime import datetime
import factory


class PollFactory(factory.DjangoModelFactory):
    owner = factory.SubFactory(UserFactory)
    remote_id = factory.Sequence(lambda n: n)

    created = datetime.now()
    votes_count = 0
    answer_id = 0

    class Meta:
        model = Poll


class AnswerFactory(factory.DjangoModelFactory):
    poll = factory.SubFactory(PollFactory)
    votes_count = 0
    rate = 0

    class Meta:
        model = Answer
