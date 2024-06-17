from django.contrib import admin
from modsoptimizer.models import CourseCode, CourseIndex, CourseProgram


class CourseProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'value', 'datetime_added']
    search_fields = ['name', 'year', 'value']
    list_filter = ['year']

admin.site.register(CourseCode)
admin.site.register(CourseIndex)
admin.site.register(CourseProgram, CourseProgramAdmin)
