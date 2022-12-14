from sso.utils import send_email


def send_feedback_submission(email, feedback):
    SUBJECT = 'SUBJECT'
    CONTENT = f'''
        content...{feedback}
    '''
    send_email(SUBJECT, CONTENT, [email])


def send_feedback_reply():
    pass
