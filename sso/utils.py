import boto3
from SUITC_Backend.settings import ses_client


def send_email(subject, body, recipients: list, sender='do-not-reply'):
    email_from = sender + '@ntusu.org'
    return ses_client.send_email(
        Source = email_from,
        Destination = {'ToAddresses': recipients},
        Message = {
            'Subject': {
                'Data': subject,
            },
            'Body': {
                'Html': {
                    'Data': body,
                }
            },
        }
    )


def send_activation_token(email, token):
    ACTIVATION_EMAIL_SUBJECT = 'NTUSU Portal Activation Link'
    ACTIVATION_EMAIL_CONTENT = f'''
        Hi,
        <br><br>
        Thank you for registering to NTUSU Portal.
        <br>
        Please confirm your email address by clicking the link below.
        <br>
        <h2>
            <a href="https://app.ntusu.org/sso/verify/{token}/">
                Validate Account
            </a>
        </h2>
        <p>
            The link above will only be valid for the next 24 hours.
            If you never registered to NTUSU Portal, please ignore this email.
        </p>
    '''
    send_email(ACTIVATION_EMAIL_SUBJECT, ACTIVATION_EMAIL_CONTENT, [email])
