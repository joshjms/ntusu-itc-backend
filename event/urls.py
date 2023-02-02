from django.urls import path
from event.views import (EventListAll, 
                         EventList, 
                         EventCreate, 
                         EventEdit,
                         AdminList,
                         AddEventAdmin,
                         AdminUpdate,
                         UserList,
                         CheckAdminStatus)
app_name = 'event'

urlpatterns = [
    path('all_events/',EventListAll.as_view(), name="event-list-all"),
    path('my_events/', EventList.as_view(), name="event-list"),
    path('create_new/', EventCreate.as_view(), name='event-create'),
    path('<int:pk>/edit/', EventEdit.as_view(), name='event-edit'),
    path('manage_admin/', AdminList.as_view(), name='admin-list'),
    path('manage_admin/add', AddEventAdmin.as_view(), name='add-event-admin'),
    path('manage_admin/<int:pk>', AdminUpdate.as_view(), name='admin-update'),
    path('manage_admin/get_user_list', UserList.as_view(), name='admin-get_user_list'),
    path('check_admin_status/', CheckAdminStatus.as_view(), name='check-admin-status')
]
