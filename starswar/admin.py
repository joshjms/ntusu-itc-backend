from django.contrib import admin
from .models import IndexSwapperConfig, XCourseIndex as CourseIndex, XSwapRequest as SwapRequest


class IndexSwapperConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not IndexSwapperConfig.objects.exists()


class SwapRequestAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'current_index',
        'status', 'wanted_indexes')


admin.site.register(IndexSwapperConfig, IndexSwapperConfigAdmin)
admin.site.register(CourseIndex)
admin.site.register(SwapRequest, SwapRequestAdmin)
