from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
import pandas as pd
from botocore.exceptions import NoCredentialsError
import io
from SUITC_Backend.settings import s3_client, EVENTS_CSV_BUCKET_NAME

from sso.models import User
from event.models import Event, EventAdmin, EventOfficer, MatricCheckIn
from event.serializers import (
    EventSerializer, 
    EventAdminSerializer, 
    AddEventAdminSerializer,
    UserSerializer, 
    EventOfficerSerializer, 
    MatricListSerializer,
    MatricCheckInSerializer,
    OfficerLoginSerializer,
)
from event.permissions import (
    IsEventAdmin, 
    IsEventCreator, 
    IsEventSuperAdmin,
    IsEventCreatorPK
)

from datetime import datetime
from collections import Counter
from event.filters import MatricCheckInFilter
from django_filters.rest_framework import DjangoFilterBackend

#GET /events/all_events/
class EventListAll(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventSuperAdmin]

#GET /events/my_events/
class EventList(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsEventAdmin]

    def get_queryset(self):
        event_admin = EventAdmin.objects.get(user=self.request.user)
        return Event.objects.filter(event_admin=event_admin)

#POST /event/create_new/
class EventCreate(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventAdmin]

    def perform_create(self, serializer):
        user = self.request.user
        event_admin = EventAdmin.objects.get(user=user)
        serializer.save(event_admin=event_admin)

#PUT /event/<int:pk>/edit/
class EventEdit(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventCreator]

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Event.objects.filter(pk=pk)

    def perform_update(self, serializer):
        serializer.save(auto_start=True, auto_end=True)

#GET /event/manage_admin/
class AdminList(generics.ListAPIView):
    queryset = EventAdmin.objects.all()
    serializer_class = EventAdminSerializer
    permission_classes = [IsEventSuperAdmin]

#POST /event/manage_admin/add/
# allow a list of EventAdmin to be added
class AddEventAdmin(generics.CreateAPIView):
    queryset = EventAdmin.objects.all()
    serializer_class = AddEventAdminSerializer
    permission_classes = [IsEventSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#PUT /event/manage_admin/<int:pk>/
class AdminUpdate(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventAdminSerializer
    permission_classes = [IsEventSuperAdmin]
    def get_queryset(self):
        pk = self.kwargs['pk']
        return EventAdmin.objects.filter(pk=pk)

#GET /event/manage_admin/get_user_list/
# get a list of emails of users that are not event admin
class UserList(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsEventSuperAdmin]
    def get_queryset(self):
        # exclude users that are event admins already
        list_user_id = list(EventAdmin.objects.values_list('user_id'))
        list_user_id = [id[0] for id in list_user_id]
        return User.objects.exclude(id__in=list_user_id)

#GET /event/check_admin_status/
class CheckAdminStatus(APIView):
    def get(self, request):
        if request.user.is_anonymous:
            return Response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(id=request.user.id)
        try:
            event_admin = EventAdmin.objects.get(user=user)
            if event_admin.is_superadmin:
                return Response('event_superadmin', status=status.HTTP_200_OK)
            else:
                return Response('event_admin', status=status.HTTP_200_OK)
        except EventAdmin.DoesNotExist:
            return Response('regular_user', status=status.HTTP_200_OK)

#POST /event/<pk>/create_officer/
class AddEventOfficer(generics.CreateAPIView):
    serializer_class = EventOfficerSerializer
    permission_classes = [IsEventCreatorPK]

    def create(self, request, pk):
        event = Event.objects.get(pk=pk)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#GET /event/edit_officer/<token>/
class EventOfficerEdit(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventOfficerSerializer
    permission_classes = [IsEventCreator]
    lookup_field = 'token'

    def get_queryset(self):
        token = self.kwargs['token']
        return EventOfficer.objects.filter(token=token)
    
#POST /event/officer_login/  
class EventOfficerLoginView(generics.GenericAPIView):
    serializer_class = OfficerLoginSerializer
    def post(self, request):
        token = request.data.get('token')
        try:
            event_officer = EventOfficer.objects.get(token=token)
        except EventOfficer.DoesNotExist:
            return Response({"detail": "Invalid officer token"}, status=status.HTTP_404_NOT_FOUND)
        event_id = event_officer.event.id
        return Response({"event_id": event_id}, status=status.HTTP_200_OK)

#POST /event/<pk>/input/
# only need to input token and matric_number
class EventInputView(generics.CreateAPIView):
    queryset = MatricCheckIn.objects.all()
    serializer_class = MatricCheckInSerializer

    def post(self, request, pk):
        # Check if id is valid
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"detail": "Invalid event id"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the event is open for check-in
        if not event.is_active:
            return Response({"detail": "This event is not yet open for check in"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the format is correct
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if the current officer is assigned to an active counter
        try:
            token = serializer.validated_data["token"]
            event_officer = EventOfficer.objects.get(token=token)
            if not event_officer.is_active:
                return Response({"detail": "You are not currently assigned to any active counter"}, status=status.HTTP_400_BAD_REQUEST)
        except EventOfficer.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the matric card is valid for the event
        matric_number = serializer.validated_data['matric_number']
        matric_prefix = matric_number[0]
        if not event.allow_exchange_student and matric_prefix == 'N':
            return Response({"detail": "Exchange students are not allowed for this event"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif not event.allow_non_undergraduate and matric_prefix == 'G':
            return Response({"detail": "This event is only open to undergraduate students"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Check if the matric card has already checked in for the event
        try:
            matric_check_in = MatricCheckIn.objects.get(event=event, matric_number=matric_number)
            return Response({"detail": f"Matric card {matric_number} already checked in at counter {matric_check_in.officer_name}"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except MatricCheckIn.DoesNotExist:
            pass
        
        #Save the check-in record
        serializer.save(event=event)
        return Response({"detail": "Successfully checked in"}, status=status.HTTP_201_CREATED)

#GET /event/<event_id>/matric_list/
class MatricList(generics.ListAPIView):
    permission_classes = [IsEventCreatorPK]
    serializer_class = MatricListSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return MatricCheckIn.objects.filter(event_id=pk)

#GET /event/<event_id>/statistics/
class EventStatistics(generics.ListAPIView):
    permission_classes = [IsEventCreatorPK]
    serializer_class = MatricListSerializer
    filter_backends = [DjangoFilterBackend]
    # filtered statistics of matric check in from officer name and 
    # from [start_date to end_date) (excluding end_date)
    filterset_class = MatricCheckInFilter

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return MatricCheckIn.objects.filter(event_id=pk)

    def get(self, request, *args, **kwargs):
        # get the list of the matric check_ins details
        matric_list = self.list(request, *args, **kwargs).data

        # calculate 
        check_in_date = [
            datetime.strptime(matric["added_date"],'%Y-%m-%d %H:%M:%S').date() 
            for matric in matric_list
        ]
        C = Counter(check_in_date)
        check_ins = [
            {
                "date": date,
                "count": count,
            } 
            for date, count in C.items()
        ]

        # calculate prefix sums of the count from check_ins
        accumulated_check_ins = []
        check_in_count = 0
        for check_in_dict in check_ins:
            check_in_count += check_in_dict['count']
            accumulated_check_ins.append(
                {
                    "date": check_in_dict['date'],
                    "count": check_in_count,
                }
            )
        
        data = {
            "matric_list": matric_list,
            "check_ins": check_ins,
            "accumulated_check_ins": accumulated_check_ins,
        }
        return Response(data, status=status.HTTP_200_OK)
    
#GET <int:pk/export_csv/
class ExportMatricCheckInsView(APIView):
    permission_classes = [IsEventCreator]

    def get(self, request, event_id):
        try:
            # Get query parameters for filtering and parse it
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

            # get all the matric of an event
            matric_check_ins = MatricCheckIn.objects.filter(event__id=event_id)   
            
            # Apply date range filtering if query parameters are provided
            if start_date:
                matric_check_ins = matric_check_ins.filter(added_date__gte=start_date)
            if end_date:
                matric_check_ins = matric_check_ins.filter(added_date__lte=end_date)

            serializer = MatricListSerializer(matric_check_ins, many=True)
            data = serializer.data
            
            # Convert the data to Excel in memory
            df = pd.DataFrame(data)
            in_memory_fp = io.BytesIO()
            df.to_excel(in_memory_fp, index=False)
            in_memory_fp.seek(0)

            # Generate a unique filename with event ID and current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f'event_{event_id}_matric_check_ins_{timestamp}.xlsx'

            # Upload the Excel file to AWS S3
            bucket_name = EVENTS_CSV_BUCKET_NAME
            s3_client.upload_fileobj(in_memory_fp, bucket_name, file_name)
            s3_link = f'https://{bucket_name}.s3.amazonaws.com/{file_name}'

            return Response({'matric_checkins_link': s3_link}, status=status.HTTP_200_OK)
        except NoCredentialsError:
            return Response({"detail": "AWS credentials are not configured correctly."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)