import boto3
from SUITC_Backend.settings import ses_client


def send_email(email_from, email_to, subject, body):
    email_from = email_from + "@ntusu.org"
    response = ses_client.send_email(
        Source=email_from,
        Destination={'ToAddresses': [email_to]},
        Message={
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
    return response
