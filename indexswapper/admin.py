from django.contrib import admin
from indexswapper.models import CourseIndex, SwapRequest


class CourseIndexAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'pending_count')


class SwapRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'current_index',
        'status', 'wanted_indexes')


admin.site.register(CourseIndex, CourseIndexAdmin)
admin.site.register(SwapRequest, SwapRequestAdmin)
