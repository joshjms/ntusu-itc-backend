from sso.utils import send_email, DO_NOT_REPLY_MESSAGE
from ufacility.models import UFacilityUser, Venue, SecurityEmail, BookingGroup


exco_email = 'su-ope@e.ntu.edu.sg'

def send_email_to_security(venue: Venue, start, end):
    if venue.is_send_security_mail and SecurityEmail.objects.exists():
        email_subject = f'Booking request for {venue.name} from {start} to {end}'
        email_body = '''\
                This is an auto-generated email to inform you that a booking has been placed for {venue} from {start_time} to {end_time}.
                Please contact {exco_email} should you have any enquiries.
                '''.format(venue=venue.name, start_time=start, end_time=end, exco_email=exco_email)
        security_emails = [security_email.email for security_email in SecurityEmail.objects.all()]
        send_email(email_subject, email_body, recipients=security_emails)

def send_verification_email_to_admins():
    email_subject = 'New User Registration'
    email_body = '''\
            This is an auto-generated email to inform you that a new user has registered for the SSO website.
            Please contact {exco_email} should you have any enquiries.
            '''.format(exco_email=exco_email)
    admins = UFacilityUser.objects.filter(is_admin=True)
    admin_emails = [admin.user.email for admin in admins]
    send_email(email_subject, email_body, recipients=admin_emails)

def send_booking_email_to_admins():
    email_subject = 'New Booking Request'
    email_body = '''\
            This is an auto-generated email to inform you that a new booking has been placed for the SSO website.
            Please contact {exco_email} should you have any enquiries.
            '''.format(exco_email=exco_email)
    admins = UFacilityUser.objects.filter(is_admin=True)
    admin_emails = [admin.user.email for admin in admins]
    send_email(email_subject, email_body, recipients=admin_emails)

def send_booking_results_accepted_email(booking_group: BookingGroup):
    booking_group.user_email
    email_subject = f'Accepted: UFacility Booking #{booking_group.id}'
    dates = [str(date) for date in booking_group.dates]
    dates_list = f'\n'.join(dates)
    email_body = f'''
Your request to book {booking_group.venue_name} is {booking_group.status}.


Dates: \n{dates_list}\n
Start Time: {booking_group.start_time}
End Time: {booking_group.end_time}
Purpose: {booking_group.purpose}


{DO_NOT_REPLY_MESSAGE}
            '''
    send_email(email_subject, email_body, recipients=[booking_group.user_email])

def send_booking_results_rejected_email(booking_group: BookingGroup): # TODO
    booking_group.user_email
    email_subject = f'Rejected: UFacility Booking #{booking_group.id}'
    dates = [str(date) for date in booking_group.dates]
    dates_list = f'\n'.join(dates)
    email_body = f'''
Your request to book {booking_group.venue_name} is {booking_group.status}.


This booking has been rejected due to either not booking three days in advance, a scheduling conflict with other bookings, or the venue being temporarily unavailable due to unforeseen circumstances.

Any enquiries please email {exco_email}

Booking Details
Dates: \n{dates_list}\n
Start Time: {booking_group.start_time}
End Time: {booking_group.end_time}
Purpose: {booking_group.purpose}


{DO_NOT_REPLY_MESSAGE}
            '''
    send_email(email_subject, email_body, recipients=[booking_group.user_email])
