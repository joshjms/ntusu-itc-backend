from SUITC_Backend.settings import ses_client


DO_NOT_REPLY_MESSAGE = f'''
    <p style="color: red;">        
        This is a system generated email, please do <b>not</b> reply
        directly to this email. If you have any other enquiries regarding
        our IT services, please contact the mail su-itc@e.ntu.edu.sg
        (Student Union Information Technology Committee).
    </p>
'''


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
    # ACTIVATION_LINK = 'https://app.ntusu.org/sso/verify/'
    ACTIVATION_LINK = 'http://localhost:3000/sso/verify/'
    ACTIVATION_EMAIL_SUBJECT = 'NTUSU Portal Activation Link'
    ACTIVATION_EMAIL_CONTENT = f'''
        Hi,
        <br><br>
        Thank you for registering to NTUSU Portal.
        <br>
        Please confirm your email address by clicking the link below.
        <br>
        <h2>
            <a href='{ACTIVATION_LINK}{token}/'>
                Validate Account
            </a>
        </h2>
        <p>
            If you never registered to NTUSU Portal, please ignore this email.
        </p>
        {DO_NOT_REPLY_MESSAGE}
    '''
    send_email(ACTIVATION_EMAIL_SUBJECT, ACTIVATION_EMAIL_CONTENT, [email])


def send_reset_token(email, token, username):
    # RESET_LINK = 'https://app.ntusu.org/sso/reset_password/'
    RESET_LINK = 'http://localhost:3000/sso/change_password/'
    RESET_EMAIL_SUBJECT = 'NTUSU Portal Reset Password Token'
    RESET_EMAIL_CONTENT = f'''
        Hi,
        <br><br>
        We received a request from you to reset your account password.
        <br>
        Username: <b>{username}</b>
        <br>
        Please click the link below to reset your password.
        <br>
        <h2>
            <a href='{RESET_LINK}{token}/'>
                Reset Password Link
            </a>
        </h2>
        <p>
            The link above will only be valid for the next 24 hours.
            Please do NOT share the link with anyone else.
            If you never made this request, please ignore this email.
        </p>
        {DO_NOT_REPLY_MESSAGE}
    '''
    send_email(RESET_EMAIL_SUBJECT, RESET_EMAIL_CONTENT, [email])
