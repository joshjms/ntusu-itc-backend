from django.contrib import admin
from .models import IndexSwapperConfig, CourseIndex, SwapRequest


class IndexSwapperConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not IndexSwapperConfig.objects.exists()
        # retVal = super().has_add_permission(request)
        # # set add permission to False, if object already exists
        # if retVal and IndexSwapperConfig.objects.exists():
        #     retVal = False
        # return retVald


class SwapRequestAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'current_index',
        'status', 'wanted_indexes')


admin.site.register(IndexSwapperConfig, IndexSwapperConfigAdmin)
admin.site.register(CourseIndex)
admin.site.register(SwapRequest, SwapRequestAdmin)
