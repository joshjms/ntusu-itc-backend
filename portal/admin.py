from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from portal.models import UpdateNote, FeedbackForm


class UpdateSummernote(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('id', 'public', 'title', 'added',)


admin.site.register(UpdateNote, UpdateSummernote)
admin.site.register(FeedbackForm)
