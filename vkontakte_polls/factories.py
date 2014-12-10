from vkontakte_users.factories import UserFactory
from models import Poll, Answer
from datetime import datetime
import factory
import random

class PollFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Poll

    owner = factory.SubFactory(UserFactory)
    remote_id = factory.Sequence(lambda n: n)

    created = datetime.now()
    votes_count = 0
    answer_id = 0

class AnswerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Answer

    poll = factory.SubFactory(PollFactory)
    votes_count = 0
    rate = 0