# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _
from vkontakte_api.admin import VkontakteModelAdmin
from models import Poll, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    can_delete = False
    fields = ('text','votes_count','rate')
    readonly_fields = fields

class PollAdmin(VkontakteModelAdmin):
    list_display = ('question','created','votes_count','post')
    list_display_links = ('question',)
#    list_filter = ('owner',)
    search_fields = ('question',)
#    exclude = ('like_users','repost_users',)
    inlines = [AnswerInline]

admin.site.register(Poll, PollAdmin)