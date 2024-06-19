from django.contrib import admin
from modsoptimizer.models import CourseCode, CourseIndex, CourseProgram, CourseCodeProgram


class CourseCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'level', 'program_code', 'name']

class CourseProgramAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'year', 'value', 'datetime_added', 'courses_count']
    search_fields = ['name', 'year', 'value']
    list_filter = ['year']
    
    def courses_count(self, obj):
        return obj.courses.count()

admin.site.register(CourseCode, CourseCodeAdmin)
admin.site.register(CourseIndex)
admin.site.register(CourseProgram, CourseProgramAdmin)
admin.site.register(CourseCodeProgram)
