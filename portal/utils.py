from django.db.models import QuerySet
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


'''
    Utility function to get the previous and next id of an instance from a queryset.
    For example, if you have queryset of id: 1 3 4 5,
    If you get instance of id 4, then previous id is 3, next id is 5
    If you get instance of id 1, then previous id is None, next id is 3
    Returns 'serializer_data' dict with 'has_prev' and 'has_next'.
'''
def get_prev_and_next_id(qs: QuerySet, instance: object, serializer_data: dict) -> dict:
    try:
        serializer_data['has_prev'] = qs.filter(id__lt=instance.id).order_by('-id').first().id
    except AttributeError:
        serializer_data['has_prev'] = None
    try:
        serializer_data['has_next'] = qs.filter(id__gt=instance.id).order_by('id').first().id
    except AttributeError:
        serializer_data['has_next'] = None
    return serializer_data
