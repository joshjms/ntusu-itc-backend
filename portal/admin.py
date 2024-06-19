from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from portal.models import UpdateNote, FeedbackForm


class UpdateSummernote(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('id', 'public', 'title', 'added',)

class FeedbackFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'title', 'email', 'acknowledged', 'resolved', 'time',)

admin.site.register(UpdateNote, UpdateSummernote)
admin.site.register(FeedbackForm, FeedbackFormAdmin)
