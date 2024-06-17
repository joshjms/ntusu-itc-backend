from django.contrib import admin
from modsoptimizer.models import CourseCode, CourseIndex, CourseProgram


class CourseProgramAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'year', 'value', 'datetime_added', 'courses_count']
    search_fields = ['name', 'year', 'value']
    list_filter = ['year']
    
    def courses_count(self, obj):
        return obj.courses.count()

admin.site.register(CourseCode)
admin.site.register(CourseIndex)
admin.site.register(CourseProgram, CourseProgramAdmin)
