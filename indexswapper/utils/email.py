from indexswapper.models import SwapRequest
from sso.utils import DO_NOT_REPLY_MESSAGE, send_email
from sso.models import User
from SUITC_Backend.constants import FE_URL


def get_contact_type_label(contact_type: str):
    mapping = dict(SwapRequest.ContactType.choices)
    return mapping.get(contact_type, 'Invalid contact type')


def get_welcome_message(user: User):
    return f'''
<p>Hi, <b>{user.display_name}!</b> (username: <b>{user.username}</b>)</p>
<p><span><br></span></p>
'''


IMPORTANT_LINKS = f'''
<p>Important Links:</p>
<p>- Check your SwapRequest status <a href="{FE_URL['indexswapper-myswaprequests']}">here</a>.</p>
<p>- Check how many people want your current index <a href="{FE_URL['indexswapper-allmodules']}">here</a>.
You can click on the pending request number to see the details.</p>
<p>- Send your feedbacks, criticism and suggestions for our service <a href="{FE_URL['portal-feedback']}">here</a>.</p>
'''


FAQS = f'''
<p style="color: purple">FAQs</p>
<p>Q: How do I perform the swap with my pair?</p>
<p>
A: Go to NTU STARS website, click on the course and select the option 'swap with peers'.
You will need to enter the username and password of your pair.
You can consider having an online meeting with your pair to perform the swap,
and you can change your password afterwards.
</p>
<p>Q: What if I my pair does not reply me at all?</p>
<p>
A: We're very sorry if that happens to you.
We are trying our best to monitor our platform and ban users who misuse our service.
You can click on 'Search Another Pair' after 24 hours of cooldown period.
</p>
<p>Q: Why there is a cooldown period?</p>
<p>
A: Once you create a SwapRequest, you need to wait for 24 hours before you can search another pair,
or create another SwapRequest with the same course code.
This is to prevent users from abusing our service.
Additionally, please allow some time for your pair to reply to you.
Only if your pair does not reply or the swap failed after 24 hours,
you can search for another pair.
</p>
<p>Q: I have another question or feedback, where can I ask?</p>
<p>
A: You can mail `su-itc@e.ntu.edu.sg` for any other questions or feedbacks.
</p>
'''


def send_swap_request_creation(swap_request: SwapRequest):
    SUBJECT = 'Index Swapper - Swap Request Creation Confirmation'
    CONTENT = f'''
{get_welcome_message(swap_request.user)}
<p>
    This is a confirmation email that your swap request has been created:
</p>
<ul>
    <li>ID: <b>#{swap_request.id}</b></li>
    <li>Course: <b>{swap_request.current_index.name} ({swap_request.current_index.code})</b></li>
    <li>Current Index: <b>{swap_request.current_index.index}</b></li>
    <li>Wanted Indexes: <b>{', '.join(swap_request.get_wanted_indexes)}</b></li>
    <li>Your Contact: <b>{swap_request.contact_info}
    ({get_contact_type_label(swap_request.contact_type)})</b></li>
</ul>
<p>
    An algorithm is currently searching a pair for you.
    You will be contacted shortly if a match is found.
    If a match is not found, you will be placed under waiting list, and will be contacted once a pair is found.
</p>
<p><br></p>
<p>Thank you for your attention.</p>
<hr>
{IMPORTANT_LINKS}
<hr>
{DO_NOT_REPLY_MESSAGE}
    '''
    return send_email(SUBJECT, CONTENT, [swap_request.user.email])


def send_swap_search_another(swap_request: SwapRequest):
    SUBJECT = 'Index Swapper - Search Another Pair Confirmation'
    CONTENT = f'''
{get_welcome_message(swap_request.user)}
<p>
    This is a confirmation email that you are searching for another pair.
    We apologize for the inconvenience that your previous pair is not working out.
    We will take necessary action to prevent irresponsible users from abusing this system.
    Here is the information of your current swap request:
</p>
<ul>
    <li>ID: <b>#{swap_request.id}</b></li>
    <li>Course: <b>{swap_request.current_index.name} ({swap_request.current_index.code})</b></li>
    <li>Current Index: <b>{swap_request.current_index.index}</b></li>
    <li>Wanted Indexes: <b>{', '.join(swap_request.get_wanted_indexes)}</b></li>
    <li>Your Contact: <b>{swap_request.contact_info}
    ({get_contact_type_label(swap_request.contact_type)})</b></li>
</ul>
<p>
    An algorithm is currently searching a pair for you.
    You will be contacted shortly if a match is found.
    If a match is not found, you will be placed under waiting list, and will be contacted once a pair is found.
</p>
<p><br></p>
<p>Thank you for your attention.</p>
<hr>
{IMPORTANT_LINKS}
<hr>
{DO_NOT_REPLY_MESSAGE}
    '''
    return send_email(SUBJECT, CONTENT, [swap_request.user.email])


def send_swap_cancel_self(swap_request: SwapRequest, is_waiting: bool = True):
    SUBJECT = 'Index Swapper - Cancel Swap Confirmation'
    CONTENT = f'''
{get_welcome_message(swap_request.user)}
<p>
    This is a confirmation email that you have <u>cancelled</u> this swap request:
</p>
<ul>
    <li>ID: <b>#{swap_request.id}</b></li>
    <li>Course: <b>{swap_request.current_index.name} ({swap_request.current_index.code})</b></li>
    <li>Current Index: <b>{swap_request.current_index.index}</b></li>
    <li>Wanted Indexes: <b>{', '.join(swap_request.get_wanted_indexes)}</b></li>
    <li>Your Contact: <b>{swap_request.contact_info}({get_contact_type_label(swap_request.contact_type)})</b></li>
    <li>Status: <b>{is_waiting and 'Waiting' or 'Searching'}</b></li>
</ul>
<p>
    {is_waiting and 
     """
     <p style="color: orange;">
Please note that you are cancelling a swap request that has been paired.
This action might cause inconvenience to the other pair, so please refrain on cancelling a paired swap request.
If you repeat such action many times, you will be banned from using this service.
     </p>
     """
     or 
     'We apologize if you cancel the swap request due to long waiting time, or if you have found another pair outside of this platform.'}
</p>
<p><br></p>
<p>Thank you for your attention.</p>
<hr>
{IMPORTANT_LINKS}
<hr>
{DO_NOT_REPLY_MESSAGE}
    '''
    return send_email(SUBJECT, CONTENT, [swap_request.user.email])


def send_swap_cancel_pair(swap_request: SwapRequest):
    SUBJECT = 'Index Swapper - Pair Cancelled Swap Request'
    CONTENT = f'''
{get_welcome_message(swap_request.user)}
<p>
    We are sorry to say that your pair has decided to cancel the swap request:
</p>
<ul>
    <li>ID: <b>#{swap_request.id}</b></li>
    <li>Course: <b>{swap_request.current_index.name} ({swap_request.current_index.code})</b></li>
    <li>Current Index: <b>{swap_request.current_index.index}</b></li>
    <li>Wanted Indexes: <b>{', '.join(swap_request.get_wanted_indexes)}</b></li>
    <li>Your Contact: <b>{swap_request.contact_info}
    ({get_contact_type_label(swap_request.contact_type)})</b></li>
</ul>
<p>
    We will take necessary action to prevent irresponsible users from abusing this system.
    As a result, your swap request is placed back under 'SEARCHING' status.
    An algorithm is currently searching a pair for you.
    You will be contacted shortly if a match is found.
    If a match is not found, you will be placed under waiting list, and will be contacted once a pair is found.
</p>
<p><br></p>
<p>Thank you for your attention.</p>
<hr>
{IMPORTANT_LINKS}
<hr>
{DO_NOT_REPLY_MESSAGE}
    '''
    return send_email(SUBJECT, CONTENT, [swap_request.user.email])


def send_swap_completed(swap_request: SwapRequest):
    # TODO - indicate who mark the swap request as completed, you or your pair?
    SUBJECT = 'Index Swapper - Swap Request Completed'
    CONTENT = f'''
{get_welcome_message(swap_request.user)}
<p>
    This is a confirmation that the swap request has been marked as completed.
</p>
<ul>
    <li>ID: <b>#{swap_request.id}</b></li>
    <li>Course: <b>{swap_request.current_index.name} ({swap_request.current_index.code})</b></li>
    <li>Current Index: <b>{swap_request.current_index.index}</b></li>
    <li>Wanted Indexes: <b>{', '.join(swap_request.get_wanted_indexes)}</b></li>
    <li>Your Contact: <b>{swap_request.contact_info}
    ({get_contact_type_label(swap_request.contact_type)})</b></li>
    <li style="color: blue;">Pair's Contact: <b>{swap_request.pair.contact_info}
    ({get_contact_type_label(swap_request.pair.contact_type)})</b></li>
    <li style="color: blue;">Index gained: <b>{swap_request.index_gained}</b></li>
</ul>
<p>
    For any other feedbacks or enquiries, please contact `su-itc@e.ntu.edu.sg`.
</p>
<p><br></p>
<p>Thank you for your attention.</p>
<hr>
{IMPORTANT_LINKS}
<hr>
{DO_NOT_REPLY_MESSAGE}
    '''
    return send_email(SUBJECT, CONTENT, [swap_request.user.email])


def send_swap_pair_found(swap_request: SwapRequest):
    # TODO - improve FAQs later
    SUBJECT = 'Index Swapper - Pair Found!'
    CONTENT = f'''
{get_welcome_message(swap_request.user)}
<p>
    A pair for your swap request is found. Here are the details:
</p>
<ul>
    <li>ID: <b>#{swap_request.id}</b></li>
    <li>Course: <b>{swap_request.current_index.name} ({swap_request.current_index.code})</b></li>
    <li>Current Index: <b>{swap_request.current_index.index}</b></li>
    <li>Wanted Indexes: <b>{', '.join(swap_request.get_wanted_indexes)}</b></li>
    <li>Your Contact: <b>{swap_request.contact_info}
    ({get_contact_type_label(swap_request.contact_type)})</b></li>
    <li style="color: blue;">Pair's Contact: <b>{swap_request.pair.contact_info}
    ({get_contact_type_label(swap_request.pair.contact_type)})</b></li>
    <li style="color: blue;">Index gained: <b>{swap_request.index_gained}</b></li>
</ul>
<p style="color: darkblue;">
    IMPORTANT !!! Please read this carefully!
    <ol>
        <li>Our service is only to match and pair users, but <b>you need to perform the swap on your own in NTU website</b>.</li>
        <li>Please contact your pair immediately, and arrange to perform the swap within 24 hours.</li>
        <li>Read the FAQs below if you have any further questions.</li>
    </ol>
</p>
<p><br></p>
<p>Thank you for your attention.</p>
<hr>
{FAQS}
<hr>
{IMPORTANT_LINKS}
<hr>
{DO_NOT_REPLY_MESSAGE}
    '''
    return send_email(SUBJECT, CONTENT, [swap_request.user.email])
