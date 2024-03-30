from datetime import datetime as dt
from typing import Iterable
from ulocker.models import Booking, Locker, ULockerAdmin, ULockerConfig
from sso.utils import send_email, DO_NOT_REPLY_MESSAGE


'''
Utility class that provides methods to get the status of lockers.
Simply call LockerStatusUtils.get_locker_status,
passing as arguments a queryset of lockers, start_month and duration.
The 'status' field will be annotated to each locker in the queryset.

Status is determined based on the following priority:
- If Locker.is_available is False, status is 'not available'.
- If there is at least one booking that overlaps with the given start_month and duration,
and the booking status is 'allocated', status is 'occupied'.
- If there is at least one booking that overlaps with the given start_month and duration,
and the booking status is 'pending', 'awaiting payment' or 'awaiting verification',
status is 'reserved'.
- Otherwise, status is 'available'.
'''
class LockerStatusUtils:
    STATUS_PRIORITY_MAP = {
        0: 'available',
        1: 'reserved',
        2: 'occupied',
        3: 'not available'
    }
    
    @staticmethod
    def get_locker_status(queryset: Iterable[Locker],
                          start_month: int=None,
                          duration: int=1) -> Iterable[Locker]:
        if start_month is None:
            start_month = dt.now().strftime('%m/%Y')
        
        for locker in queryset:
            if locker.is_available == False:
                locker.status = LockerStatusUtils.STATUS_PRIORITY_MAP[3]
                continue
            
            status_number = 0
            bookings = Booking.objects.filter(locker=locker)
            for booking in bookings:
                if LockerStatusUtils.check_overlap(booking.start_month, booking.duration, start_month, duration):
                    if booking.status in ['allocated']:
                        status_number = max(status_number, 2)
                    elif booking.status in ['pending', 'approved - awaiting payment', 'approved - awaiting verification']:
                        status_number = max(status_number, 1)
                    else:
                        status_number = max(status_number, 0)
                        
            locker.status = LockerStatusUtils.STATUS_PRIORITY_MAP[status_number]
        return queryset
    
    @staticmethod         
    def calculate_end_month(start_month, duration):
        start_month = start_month.split('/')
        month = int(start_month[0])
        year = int(start_month[1])
        duration = int(duration)
        month += duration - 1
        while month > 12:
            month -= 12
            year += 1
        return f'{month:02d}/{year}'

    @staticmethod
    def check_overlap(start_month1, duration1, start_month2, duration2):
        end_month1 = LockerStatusUtils.calculate_end_month(start_month1, duration1)
        end_month2 = LockerStatusUtils.calculate_end_month(start_month2, duration2)
        if start_month1 == start_month2 or end_month1 == end_month2:
            return True
        if start_month1 < start_month2:
            return end_month1 >= start_month2
        else:
            return end_month2 >= start_month1

'''
- send_creation_email:
send email to ulocker admins when a new user is created
- send_payment_email:
send email to user when a Booking is approved and awaiting payment
- send_verification_email:
send email to ulocker admins requesting verification after payment is made
- send_allocation_email:
send email to user and ulocker admins when a Booking is allocated
'''
class ULockerEmailService:
    @staticmethod
    def send_creation_email(*args):
        admins = ULockerAdmin.objects.all()
        locker = Locker.objects.get(id=args[0]['locker'])
        recipients = [admin.user.email for admin in admins if admin.is_send_creation_email]
        email_subject = 'ULocker - New Booking'
        email_body = f'''
Dear ULocker Admin,<br>
<br><br>
A new locker booking has been created. Here are the details:<br>
<br>
Locker Name: {locker.name}<br>
Start Month: {args[0]['start_month']}<br>
Duration: {args[0]['duration']}<br>
Applicant Name: {args[0]['applicant_name']}<br>
Matriculation Number: {args[0]['matric_no']}<br>
Phone Number: {args[0]['phone_no']}<br>
Organization Name: {args[0]['organization_name']}<br>
Position: {args[0]['position']}<br>
<br>
Please confirm the booking above.<br>
<br><br>
{DO_NOT_REPLY_MESSAGE}
        '''
        send_email(email_subject, email_body, recipients=recipients)
        
    @staticmethod
    def send_payment_email(obj):
        config = ULockerConfig.objects.first()
        price = config.monthly_price if obj.duration == 1 \
            else config.semesterly_price if obj.duration == 4 \
            else config.yearly_price if obj.duration == 12 \
            else 'N/A'
        frontend_link = 'TODO'
        recipients = [obj.user.email]
        email_subject = 'ULocker - Payment Required'
        email_body = f'''
Dear User (username: ${obj.user.username}),<br>
<br><br>
Your locker booking has been approved. Here are the details:<br>
<br>
Locker Name: {obj.locker.name}<br>
Start Month: {obj.start_month}<br>
Duration: {obj.duration}<br>
Applicant Name: {obj.applicant_name}<br>
Matriculation Number: {obj.matric_no}<br>
Phone Number: {obj.phone_no}<br>
Organization Name: {obj.organization_name}<br>
Position: {obj.position}<br>
<br>
The price for the booking is <b>{price}</b>.<br>
Please proceed and make payment on the following link: {frontend_link}<br>
<br><br>
{DO_NOT_REPLY_MESSAGE}
        '''
        send_email(email_subject, email_body, recipients=recipients)
    
    @staticmethod
    def send_verification_email(obj):
        admins = ULockerAdmin.objects.all()
        recipients = [admin.user.email for admin in admins if admin.is_send_creation_email]
        email_subject = 'ULocker - Booking Verification Required'
        email_body = f'''
Dear ULocker Admin,<br>
<br><br>
Payment has been made for the following booking. Here are the details:<br>
<br>
Locker Name: {obj.locker.name}<br>
Start Month: {obj.start_month}<br>
Duration: {obj.duration}<br>
Applicant Name: {obj.applicant_name}<br>
Matriculation Number: {obj.matric_no}<br>
Phone Number: {obj.phone_no}<br>
Organization Name: {obj.organization_name}<br>
Position: {obj.position}<br>
<br>
Please verify the booking above.<br>
<br><br>
{DO_NOT_REPLY_MESSAGE}
        '''
        send_email(email_subject, email_body, recipients=recipients)
    
    @staticmethod
    def send_allocation_email(obj):
        admins = ULockerAdmin.objects.all()
        recipients = [admin.user.email for admin in admins if admin.is_send_creation_email]
        recipients.append(obj.user.email)
        email_subject = 'ULocker - Booking Allocated'
        email_body = f'''
Dear User (username: ${obj.user.username}),<br>
<br><br>
Your locker booking has been allocated. Here are the details:<br>
<br>
Locker Name: {obj.locker.name}<br>
Start Month: {obj.start_month}<br>
Duration: {obj.duration}<br>
Applicant Name: {obj.applicant_name}<br>
Matriculation Number: {obj.matric_no}<br>
Phone Number: {obj.phone_no}<br>
Organization Name: {obj.organization_name}<br>
Position: {obj.position}<br>
<br>
Your locker passcode is: {obj.locker.passcode}<br>
<br><br>
{DO_NOT_REPLY_MESSAGE}
        '''
        send_email(email_subject, email_body, recipients=recipients)
