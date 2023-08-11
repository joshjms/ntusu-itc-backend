from sso.utils import send_email, DO_NOT_REPLY_MESSAGE
from ufacility.models import UFacilityUser, Venue, SecurityEmail, BookingGroup


exco_email = 'su-ope@e.ntu.edu.sg'
FE_MANAGE_VERIFICATION_LINK = 'https://app.ntusu.org/ufacility/admin/verifications'

def send_email_to_security(booking_group: BookingGroup):
    if booking_group.venue.is_send_security_mail and SecurityEmail.objects.exists():
        email_subject = f'Booking of {booking_group.venue} by {booking_group.user_cca}'
        dates = [str(date) for date in booking_group.dates]
        dates_list = f'<br>'.join(dates)
        email_body = f'''
{booking_group.user_cca} is booking {booking_group.venue} for {booking_group.pax} pax.<br><br>
Dates: <br>{dates_list}<br>
Purpose: {booking_group.purpose}<br>
Start Time: {booking_group.start_time}<br>
End Time: {booking_group.end_time}<br><br>
Please program the room to open accordingly.<br><br>
Thank you.<br><br>
Best Regards,<br>
NTUSU Operations Executive<br><br>
{DO_NOT_REPLY_MESSAGE}
                '''
        security_emails = [security_email.email for security_email in SecurityEmail.objects.all()]
        send_email(email_subject, email_body, recipients=security_emails)

def send_verification_email_to_admins():
    email_subject = 'UFacility New User Registration'
    email_body = f'''\
This is an auto-generated email to inform you that a new user has request access for UFacility.
Click <a href="{FE_MANAGE_VERIFICATION_LINK}">here</a> to view.
            '''
    admins = UFacilityUser.objects.filter(is_admin=True)
    admin_emails = [admin.user.email for admin in admins]
    send_email(email_subject, email_body, recipients=admin_emails)

def send_booking_results_accepted_email(booking_group: BookingGroup):
    booking_group.user_email
    email_subject = f'Accepted: UFacility Booking #{booking_group.id}'
    dates = [str(date) for date in booking_group.dates]
    dates_list = f'<br>'.join(dates)
    email_body = f'''
Your request to book {booking_group.venue_name} is {booking_group.status}.<br><br>
Dates: <br>{dates_list}<br>
Start Time: {booking_group.start_time}<br>
End Time: {booking_group.end_time}<br>
Purpose: {booking_group.purpose}<br><br>
{DO_NOT_REPLY_MESSAGE}
            '''
    send_email(email_subject, email_body, recipients=[booking_group.user_email])

def send_booking_results_rejected_email(booking_group: BookingGroup): # TODO
    booking_group.user_email
    email_subject = f'Rejected: UFacility Booking #{booking_group.id}'
    dates = [str(date) for date in booking_group.dates]
    dates_list = f'<br>'.join(dates)
    email_body = f'''
Your request to book {booking_group.venue_name} is {booking_group.status}.<br><br>
This booking has been rejected due to either not booking three days in advance, a scheduling conflict with other bookings, or the venue being temporarily unavailable due to unforeseen circumstances.<br><br>
Any enquiries please email {exco_email}<br><br>
Booking Details<br>
Dates: <br>{dates_list}<br>
Start Time: {booking_group.start_time}<br>
End Time: {booking_group.end_time}<br>
Purpose: {booking_group.purpose}<br><br>
{DO_NOT_REPLY_MESSAGE}
            '''
    send_email(email_subject, email_body, recipients=[booking_group.user_email])
