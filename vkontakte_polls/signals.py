# -*- coding: utf-8 -*-
import logging
import re

from django.db.models.signals import post_save
from django.dispatch import receiver
from vkontakte_api.api import VkontakteError
from vkontakte_wall.models import Post

log = logging.getLogger('vkontakte_polls')


@receiver(post_save, sender=Post)
def fetch_poll_for_post(sender, instance, created, **kwargs):
    from .models import Poll
    try:
        poll_id = None
        if instance.raw_html:
            # parser way
            #<input type="hidden" id="post_poll_id-45346748_4" value="72195917" />
            #<input type="hidden" id="post_poll_raw-16297716_190770" value="-16297716_83838453" /><input type="hidden" id="post_poll_open-16297716_190770" value="1" />
            poll_id = re.findall(
                r'<input type="hidden" id="post_poll_(?:raw|id)(?:[^"]+)" value="([^"]+)" />', instance.raw_html)[0]

            if '_' in poll_id:
                poll_id = poll_id.split('_')[1]
                if poll_id:
                    Poll.remote.fetch(poll_id, instance)

        elif instance.raw_json:
            # api way
            if 'copy_history' in instance.raw_json and len(instance.raw_json['copy_history']) >= 1:
                attachments = instance.raw_json['copy_history'][0].get('attachments', [])
            else:
                attachments = instance.raw_json.get('attachments', [])

            for attachment in attachments:
                if attachment['type'] == 'poll':
                    poll = Poll.remote.parse_response_dict(attachment['poll'], {'post_id': instance.pk})
                    Poll.remote.get_or_create_from_instance(poll)

    except VkontakteError, e:
        log.error("Vkontakte error (code = %s) raised: '%s'" % (e.code, e.description))
    except (IndexError, AssertionError):
        pass
