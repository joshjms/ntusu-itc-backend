from sso.utils import send_email, DO_NOT_REPLY_MESSAGE
from portal.models import FeedbackForm


def send_feedback_confirmation(feedback: dict):
    SUBJECT = 'NTUSU ITC Feedback Confirmation'
    CONTENT = f'''
        Hi,
        <br><br>
        This is an acknowledgement email that we have received your feedback
        through NTUSU ITC Portal. The details are follows: <br>
        Type          : {FeedbackForm.Type(feedback['type']).name} <br>
        Title         : {feedback['title']} <br>
        Details       : {feedback['details']} <br>
        <br>
        Thank you for providing us these information, we will get back
        to you soon if needed. The information you provided are really
        useful for our team to improve. <br>
        <br>
        {DO_NOT_REPLY_MESSAGE}
    '''
    send_email(SUBJECT, CONTENT, [feedback['email']])


def send_feedback_reply(instance: FeedbackForm, response: str):
    SUBJECT = 'NTUSU ITC Feedback Response'
    CONTENT = f'''
        {response}
        <br>
        {DO_NOT_REPLY_MESSAGE}
    '''
    send_email(SUBJECT, CONTENT, [instance.email])
