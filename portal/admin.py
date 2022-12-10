from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from portal.models import UpdateNote


class UpdateSummernote(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('id', 'title', 'date',)


admin.site.register(UpdateNote, UpdateSummernote)
