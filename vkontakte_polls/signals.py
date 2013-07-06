# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver
from vkontakte_wall.models import Post
from vkontakte_api.utils import VkontakteError
from models import Poll
import re
import logging

log = logging.getLogger('vkontakte_polls')

@receiver(post_save, sender=Post)
def fetch_poll_for_post(sender, instance, created, **kwargs):
    try:

        poll_id = None
        if instance.raw_html:
            # parser way
            #<input type="hidden" id="post_poll_id-45346748_4" value="72195917" />
            #<input type="hidden" id="post_poll_raw-16297716_190770" value="-16297716_83838453" /><input type="hidden" id="post_poll_open-16297716_190770" value="1" />
            poll_id = re.findall(r'<input type="hidden" id="post_poll_(?:raw|id)(?:[^"]+)" value="([^"]+)" />', instance.raw_html)[0]

            if '_' in poll_id:
                poll_id = poll_id.split('_')[1]

        elif instance.raw_json:
            # api way
            for attachment in instance.raw_json.get('attachments', []):
                if attachment['type'] == 'poll':
                    poll_id = attachment['poll']['poll_id']

        assert poll_id
        Poll.remote.fetch(int(poll_id), instance)

    except VkontakteError, e:
        log.error("Vkontakte error (code = %s) raised: '%s'" % (e.code, e.description))
    except (IndexError, AssertionError):
        pass