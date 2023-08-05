from django.utils import timezone as tz
from indexswapper.utils import email
from indexswapper.utils.decorator import lock_db_table
from indexswapper.models import CourseIndex, SwapRequest


@lock_db_table(SwapRequest)
def perform_pairing(swap_request_id: int, *args, **kwargs):
    '''
    ### IMPORTANT WARNING !!! ###
    TLDR; this function should only be called one at a time,
    even if db accept multiple connection & server has multiple threads / instances
    If this function is called multiple times at the same time,
    it may cause the same swap request to be paired with multiple swap requests

    This function is to be called:
    - when a new swap request is created
        (call with that swap request id)
    - when a pair has been matched, but one side cancel it
        (call with the swap request id of the other side)
    - when a pair has been matched, swap unsuccessful after cooldown,
        and one side reinitiate the search
        (call with this user's swap request id, no need to do for the other side)

    Pseudocode:
    - Make this SwapRequest status to SEARCHING (it may be 'WAITING'), reset some other values
    - Filter all swap request that has status of waiting, has the same course code,
        and exclude this swap request
    - For each instance of the filtered swap request:
        - If this swap request's current index is in the instance's wanted indexes,
            and the instance's current index is in this swap request's wanted indexes,
            then:
            - Fill in the 'pair', 'index_gained', 'datetime_found' column for both swap requests
            - Set both swap requests' status to WAITING
            - Return True
    - Otherwise return False
    '''
    swap_request = SwapRequest.objects.get(id=swap_request_id)
    swap_request.status = SwapRequest.Status.SEARCHING
    swap_request.index_gained = ''
    swap_request.pair = None
    swap_request.datetime_found = None
    instances = SwapRequest.objects.filter(
        status=SwapRequest.Status.SEARCHING,
        current_index__code=swap_request.current_index.code)\
        .exclude(id=swap_request_id)
    for instance in instances:
        if instance.current_index.index in swap_request.get_wanted_indexes and\
                swap_request.current_index.index in instance.get_wanted_indexes:
            swap_request.status = SwapRequest.Status.WAITING
            instance.status = SwapRequest.Status.WAITING
            swap_request.pair = instance
            instance.pair = swap_request
            swap_request.index_gained = instance.current_index.index
            instance.index_gained = swap_request.current_index.index
            found_time = tz.now()
            swap_request.datetime_found = found_time
            instance.datetime_found = found_time
            swap_request.save()
            instance.save()
            for i in [swap_request, instance]:
                for index in i.get_wanted_indexes:
                    course_index = CourseIndex.objects.get(index=index)
                    course_index.pending_count -= 1
                    course_index.save()
            email.send_swap_pair_found(swap_request)
            email.send_swap_pair_found(instance)
            return True
    swap_request.save()
    return False
