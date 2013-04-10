# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver
from vkontakte_wall.models import Post
from models import Poll
import re

@receiver(post_save, sender=Post)
def parse_poll(sender, instance, created, **kwargs):
    try:
        #<input type="hidden" id="post_poll_id-45346748_4" value="72195917" />
        #<input type="hidden" id="post_poll_raw-16297716_190770" value="-16297716_83838453" /><input type="hidden" id="post_poll_open-16297716_190770" value="1" />
        poll_id = re.findall(r'<input type="hidden" id="post_poll_(?:raw|id)(?:[^"]+)" value="([^"]+)" />', instance.raw_html)[0]
        if '_' in poll_id:
            poll_id = poll_id.split('_')[1]
        owner = instance.copy_owner or instance.wall_owner
        Poll.remote.fetch(int(poll_id), owner, instance)
    except IndexError:
        pass