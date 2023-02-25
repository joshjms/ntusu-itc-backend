from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins, status, viewsets
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from ufacility.models import Verification, Venue, UFacilityUser, Booking2, BookingGroup, SecurityEmail
from ufacility.serializers import (
    BookingGroupSerializer,
    UFacilityUserSerializer,
    VerificationSerializer,
    BookingPartialSerializer,
    VenueSerializer,
    SecurityEmailSerializer,
)
from ufacility.permissions import (
    IsAuthenticated,
    IsUFacilityUser,
    IsUFacilityAdmin,
    IsUFacilityInstanceOwnerOrAdmin,
    IsUserInstanceOwnerOrAdmin,
    IsPendingBookingOrAdmin,
)
from ufacility.utils import decorators, generics as custom_generics, mixins as custom_mixins
from sso.models import User


# GET, POST /ufacility/booking_group/ TODO
class BookingGroupView(custom_mixins.BookingGroupUtilMixin, generics.ListCreateAPIView):
    serializer_class = BookingGroupSerializer
    permission_classes = [IsUFacilityUser]

    def get_queryset(self):
        ufacility_user = UFacilityUser.objects.get(user=self.request.user)
        return BookingGroup.objects.filter(user=ufacility_user).order_by('id')

    def perform_create(self, serializer):
        ufacility_user = get_object_or_404(UFacilityUser, user=self.request.user)
        booking_group = serializer.save(user=ufacility_user)
        for date in booking_group.dates:
            Booking2.objects.create(
                **serializer.serialize_to_booking(date)
            )

# GET /ufacility/booking_group/admin/ TODO
class BookingGroupAdminView(custom_mixins.BookingGroupUtilMixin, generics.ListAPIView):
    queryset = BookingGroup.objects.all()
    serializer_class = BookingGroupSerializer
    permission_classes = [IsUFacilityAdmin]

# PUT, DELETE /ufacility/booking_group/<bookinggroup_id>/ TODO
class BookingGroupDetailView(custom_generics.UpdateDestroyAPIView):
    queryset = BookingGroup.objects.all()
    serializer_class = BookingGroupSerializer
    permission_classes = [IsUFacilityInstanceOwnerOrAdmin, IsPendingBookingOrAdmin]
    lookup_url_kwarg = 'bookinggroup_id'

# PUT /ufacility/booking_group/<bookinggroup_id>/accept/ TODO
class BookingGroupAcceptView(APIView):
    permission_classes = [IsUFacilityAdmin]

    @decorators.pending_booking_group_only
    def put(self, request, *args, **kwargs):
        BookingGroupSerializer(kwargs['booking_group']).accept_booking_group()
        return Response({'message': 'Booking group accepted.'}, status=status.HTTP_200_OK)

# PUT /ufacility/booking_group/<bookinggroup_id>/reject/ TODO
class BookingGroupRejectView(APIView):
    permission_classes = [IsUFacilityAdmin]

    @decorators.pending_booking_group_only
    def put(self, request, *args, **kwargs):
        BookingGroupSerializer(kwargs['booking_group']).reject_booking_group()
        return Response({'message': 'Booking group rejected.'}, status=status.HTTP_200_OK)

# GET /ufacility/check_user_status/
class CheckStatusView(APIView):
    def get(self, request):
        if not request.user.is_anonymous: ufacilityuser = UFacilityUser.objects.filter(user=request.user).first()
        user_type = ''
        if request.user.is_anonymous: user_type = 'anonymous'
        elif not ufacilityuser: user_type = 'sso user'
        elif not ufacilityuser.is_admin: user_type = 'ufacility user'
        else: user_type = 'ufacility admin'
        return Response({'type': user_type}, status=status.HTTP_200_OK)

# GET, PUT /ufacility/users/<user_id>/
class UFacilityUserDetailView(generics.RetrieveUpdateAPIView):
    queryset = UFacilityUser.objects.all()
    serializer_class = UFacilityUserSerializer
    permission_classes = [IsUserInstanceOwnerOrAdmin]
    lookup_url_kwarg = 'user_id'

    def get(self, request, *args, **kwargs):
        if kwargs[self.lookup_url_kwarg] == 0:
            user = User.objects.get(id=request.user.id)
            instance = get_object_or_404(UFacilityUser, user=user)
            sr = self.get_serializer_class()(instance)
            return Response(sr.data)
        return super().get(request, *args, **kwargs)

# GET, POST /ufacility/verifications/
class VerificationView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer

    def get_permissions(self):
        return [IsUFacilityAdmin()] if self.request.method == 'GET' else [IsAuthenticated()]
    
    def get(self, request, *args, **kwargs):
        verifications = Verification.objects.all()
        filter_status = request.GET.get('status', '')
        if filter_status: verifications = verifications.filter(status__in=filter_status.split('-'))
        serializer = VerificationSerializer(verifications, many=True)
        return Response(serializer.data)

    @method_decorator(decorators.no_verification_and_ufacility_account)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# GET, DELETE /ufacility/verifications/<verification_id>/
class VerificationDetailView(generics.RetrieveDestroyAPIView):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
    lookup_url_kwarg = 'verification_id'
    
    def get_permissions(self):
        return [IsUFacilityInstanceOwnerOrAdmin() if self.request.method == 'GET' else IsUFacilityAdmin()]
    
    def get(self, request, *args, **kwargs):
        if kwargs[self.lookup_url_kwarg] == 0:
            user = User.objects.get(id=request.user.id)
            instance = get_object_or_404(Verification, user=user)
            sr = self.get_serializer_class()(instance)
            return Response(sr.data)
        return super().get(request, *args, **kwargs)

# PUT /ufacility/verifications/<verification_id>/accept/
class VerificationAcceptView(APIView):
    permission_classes = [IsUFacilityAdmin]

    def put(self, request, *args, **kwargs):
        verification = get_object_or_404(Verification, id=kwargs['verification_id'])
        verification.status = 'accepted'
        verification.save()
        if UFacilityUser.objects.filter(user=verification.user).count() == 0:
            UFacilityUser.objects.create(
                user=verification.user,
                is_admin=False,
                **model_to_dict(verification, fields=['cca', 'hongen_name', 'hongen_phone_number'])
            )
            return Response({'message': 'Verification accepted.'})
        return Response({'message': 'Verication has been accepted and ufacility user model existed.'},
            status=status.HTTP_409_CONFLICT)

# PUT /ufacility/verifications/<verification_id>/reject/
class VerificationRejectView(APIView):
    permission_classes = [IsUFacilityAdmin]

    def put(self, request, *args, **kwargs):
        verification = get_object_or_404(Verification, id=kwargs['verification_id'])
        if verification.status == 'declined':
            UFacilityUser.objects.filter(user=verification.user).delete() # just in case
            return Response({'message': 'Verification has been declined and no such ufacility user model.'},
                status=status.HTTP_409_CONFLICT)
        verification.status = 'declined'
        verification.save()
        deleted, _ = UFacilityUser.objects.filter(user=verification.user).delete()
        if deleted == 1:
            return Response({'message': 'Access revoked.'})
        return Response({'message': 'Verification rejected.'})

# GET /bookings/<int:venue_id>/<str:date>/
class BookingHourlyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, venue_id, date):
        venue = get_object_or_404(Venue, id=venue_id)
        try:
            year, month, day = int(date[:4]), int(date[5:7]), int(date[8:])
            bookings = Booking2.objects.filter(Q(venue=venue), Q(date__year=year), Q(date__month=month), Q(date__day=day), Q(status='pending') | Q(status='accepted'))
            serializer = BookingPartialSerializer(bookings, many=True)
            return Response(serializer.data)
        except:
            return Response({'error': 'please adhere to the date format YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

# GET, POST /ufacility/venue/ (venue-list)
# GET, PUT, PATCH, DELETE /ufacility/venue/<pk>/ (venue-detail)
class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    
    def get_permissions(self):
        return [(IsAuthenticated() if self.request.method == 'GET' else IsUFacilityAdmin())]

# GET, POST /ufacility/email/ (email-list)
# GET, PUT, PATCH, DELETE /ufacility/email/<pk>/ (email-detail)
class EmailViewSet(viewsets.ModelViewSet):
    queryset = SecurityEmail.objects.all()
    serializer_class = SecurityEmailSerializer
    permission_classes = [IsUFacilityAdmin]
