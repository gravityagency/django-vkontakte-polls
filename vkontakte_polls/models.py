# -*- coding: utf-8 -*-
from django.db import models
#from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from vkontakte_api.models import VkontakteManager, VkontakteModel  # , VkontakteContentError
from vkontakte_api.parser import VkontakteParser
from vkontakte_api.utils import api_call, ACCESS_TOKEN
#from vkontakte_api.decorators import fetch_all
from vkontakte_users.models import User, USER_FIELDS
from vkontakte_groups.models import Group
from vkontakte_wall.models import Post
#from datetime import datetime
import logging

log = logging.getLogger('vkontakte_polls')


class AnswerManager(models.Manager):
    pass


class PollManager(models.Manager):
    pass


class PollsRemoteManager(VkontakteManager):
    pass


class PollRemoteManager(PollsRemoteManager):

    def fetch(self, poll_id, post, **kwargs):
        owner = post.copy_owner or post.wall_owner

        kwargs['extra_fields'] = {'post_id': post.id}
        kwargs['poll_id'] = poll_id
        kwargs['owner_id'] = owner.remote_id
        if isinstance(owner, Group):
            kwargs['owner_id'] *= -1
        return super(PollRemoteManager, self).fetch(**kwargs)


class AnswerRemoteManager(PollsRemoteManager):
    pass


class PollsAbstractModel(VkontakteModel):
    class Meta:
        abstract = True

    methods_namespace = 'polls'
    remote_id = models.BigIntegerField(u'ID', help_text=u'Уникальный идентификатор', primary_key=True)


class Poll(PollsAbstractModel):
    class Meta:
        verbose_name = u'Опрос Вконтакте'
        verbose_name_plural = u'Опросы Вконтакте'
        ordering = ['created']

    remote_pk_field = 'poll_id'

    # Владелец головосвания User or Group
    owner_content_type = models.ForeignKey(ContentType, related_name='vkontakte_polls_polls')
    owner_id = models.PositiveIntegerField(db_index=True)
    owner = generic.GenericForeignKey('owner_content_type', 'owner_id')

    post = models.OneToOneField(Post, verbose_name=u'Сообщение, в котором опрос', related_name='poll')

    created = models.DateTimeField(u'Дата создания', db_index=True)
    question = models.TextField(u'Вопрос')
    votes_count = models.PositiveIntegerField(u'Голосов', help_text=u'Общее количество ответивших пользователей', db_index=True)

    answer_id = models.PositiveIntegerField(u'Ответ', help_text=u'идентификатор ответа текущего пользователя')

    objects = PollManager()
    remote = PollRemoteManager(remote_pk=('remote_id',), methods={
        'get': 'getById',
    })

    _answers = []

    @property
    def slug(self):
        return '%s?w=poll-%s' % (self.owner.screen_name, self.post.remote_id)

    def __unicode__(self):
        return self.question

    def parse(self, response):
        response['votes_count'] = response.pop('votes')

        # answers
        self._answers = [Answer.remote.parse_response(answer) for answer in response.pop('answers')]

        # owner
        owner_id = response.pop('owner_id')
        ct_model = User if owner_id > 0 else Group
        self.owner_content_type = ContentType.objects.get_for_model(ct_model)
        try:
            self.owner_id = self.owner_content_type.get_object_for_this_type(remote_id=abs(owner_id)).id
        except ObjectDoesNotExist:
            raise ValueError("Impossible to parse poll with unexisted owner %s, remote_id=%s" % (self.owner_content_type.model, owner_id))

        return super(Poll, self).parse(response)

    def save(self, *args, **kwargs):
        result = super(Poll, self).save(*args, **kwargs)

        for answer in self._answers:
            answer.poll = self
            answer.save()
        self._answers = []

        return result


class Answer(PollsAbstractModel):
    class Meta:
        verbose_name = u'Ответ опроса Вконтакте'
        verbose_name_plural = u'Ответы опросов Вконтакте'
        ordering = ['remote_id']

    poll = models.ForeignKey(Poll, verbose_name=u'Опрос', related_name='answers')
    text = models.TextField(u'Текст ответа')
    votes_count = models.PositiveIntegerField(u'Голосов', help_text=u'Количество пользователей, проголосовавших за ответ', db_index=True)
    rate = models.FloatField(u'Рейтинг', help_text=u'Рейтинг ответа, в %')

    voters = models.ManyToManyField(User, verbose_name=u'Голосующие', blank=True, related_name='poll_answers')

    objects = AnswerManager()
    remote = AnswerRemoteManager()

    def __unicode__(self):
        return self.text

    def parse(self, response):
        response['votes_count'] = response.pop('votes')

        super(Answer, self).parse(response)

    def fetch_voters(self, offset=0, source='api'):
        if source == 'api':
            return self.fetch_voters_by_api(offset)
        return self.fetch_voters_by_parser(offset)

    def fetch_voters_by_parser(self, offset=0):
        '''
        Update and save fields:
            * votes_count - count of likes
        Update relations:
            * voters - users, who vote for this answer
        '''
        post_data = {
            'act': 'poll_voters',
            'al': 1,
            'opt_id': self.pk,
            'post_raw': self.poll.post.remote_id,
        }

        number_on_page = 40
        if offset != 0:
            post_data['offset'] = '%d,0,0,0,0,0,0,0,0' % offset

        log.debug('Fetching votes of answer ID="%s" of poll %s of post %s of group "%s", offset %d' % (self.pk, self.poll.pk, self.poll.post, self.poll.owner, offset))

        parser = VkontakteParser().request('/al_wall.php', data=post_data)

        if offset == 0:
            try:
                self.votes_count = int(parser.content_bs.find('span', {'id': 'wk_poll_row_count0'}).text)
                self.rate = float(parser.content_bs.find('b', {'id': 'wk_poll_row_percent0'}).text.replace('%', ''))
                self.save()
            except:
                log.warning('Strange markup of first page votes response: "%s"' % parser.content)
            self.voters.clear()

        #<div class="wk_poll_voter inl_bl">
        #  <div class="wk_pollph_wrap" onmouseover="WkPoll.bigphOver(this, 159699623)">
        #    <a class="wk_poll_voter_ph" href="/chitos2">
        #      <img class="wk_poll_voter_img" src="http://cs406722.vk.me/v406722623/6ca9/zpmoGDj_z_c.jpg" />
        #    </a>
        #  </div>
        #  <div class="wk_poll_voter_name"><a class="wk_poll_voter_lnk" href="/chitos2">Владислав Калакутский</a></div>
        #</div>

        items = parser.add_users(users=('div', {'class': 'wk_poll_voter inl_bl'}),
            user_link=('a', {'class': 'wk_poll_voter_lnk'}),
            user_photo=('img', {'class': 'wk_poll_voter_img'}),
            user_add=lambda user: self.voters.add(user))

        if len(items) == number_on_page:
            return self.fetch_voters(offset=offset + number_on_page)
        else:
            return self.voters.all()

    def fetch_voters_by_api(self, offset=0):
        '''
        Update and save fields:
            * votes_count - count of likes
        Update relations:
            * voters - users, who vote for this answer
        '''
        number_on_page = 100
        params = {
            'owner_id': self.poll.post.remote_id.split('_')[0],
            'poll_id': self.poll.pk,
            'answer_ids': self.pk,
            'offset': offset,
            'count': number_on_page,
            'fields': USER_FIELDS,
        }

        result = api_call('polls.getVoters', used_access_tokens=ACCESS_TOKEN, **params)[0]

        if offset == 0:
            try:
                self.votes_count = int(result['users'][0])
                pp = Poll.remote.fetch(self.poll.pk, self.poll.post)
                if pp and pp.votes_count:
                    self.rate = (float(self.votes_count) / pp.votes_count) * 100
                else:
                    self.rate = 0
                self.save()
            except Exception, err:
                log.warning('Answer fetching error with message: %s' % err)
            self.voters.clear()

        for user in User.remote.parse_response_list(result['users'][1:], extra_fields={}):
            user = User.remote.get_or_create_from_instance(user)
            self.voters.add(user)

        if len(result['users'][1:]) == number_on_page:
            return self.fetch_voters_by_api(offset + number_on_page)
        return self.voters.all()


import signals
