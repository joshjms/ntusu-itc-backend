from sso.utils import send_email
from ufacility.models import UFacilityUser


exco_email = ""

def send_email_to_security(venue, start, end):
    email_subject = f"Booking request for {venue.name} from {start} to {end}"
    email_body = """\
            This is an auto-generated email to inform you that a booking has been placed for {venue} from {start_time} to {end_time}.
            Please contact {exco_email} should you have any enquiries.
            """.format(venue=venue.name, start_time=start, end_time=end, exco_email=exco_email)
    send_email(email_subject, email_body, recipients=[venue.security_email])

def send_verification_email_to_admins():
    email_subject = "New User Registration"
    email_body = """\
            This is an auto-generated email to inform you that a new user has registered for the SSO website.
            Please contact {exco_email} should you have any enquiries.
            """.format(exco_email=exco_email)
    admins = UFacilityUser.objects.filter(is_admin=True)
    admin_emails = []
    for admin in admins:
        admin_emails.append(admin.user.email)
    send_email(email_subject, email_body, recipients=admin_emails)

def send_booking_email_to_admins():
    email_subject = "New Booking Request"
    email_body = """\
            This is an auto-generated email to inform you that a new booking has been placed for the SSO website.
            Please contact {exco_email} should you have any enquiries.
            """.format(exco_email=exco_email)
    admins = UFacilityUser.objects.filter(is_admin=True)
    admin_emails = []
    for admin in admins:
        admin_emails.append(admin.user.email)
    send_email(email_subject, email_body, recipients=admin_emails)

def send_booking_results_email(email, venue, start, end, status):
    email_subject = f"Booking request for {venue.name} from {start} to {end} has been {status}"
    email_body = """\
            This is an auto-generated email to inform you that your booking has been {status}.
            Please contact {exco_email} should you have any enquiries.
            """.format(status=status, exco_email=exco_email)
    send_email(email_subject, email_body, recipients=[email])
