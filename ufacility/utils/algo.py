from django.db.models import QuerySet
from ufacility.models import Booking2, BookingGroup
from datetime import timedelta as td, date, time


def clash_exists(venue, date, start_time, end_time):
    bookings = Booking2.objects.filter(venue=venue, date=date)
    for booking in bookings:
        if start_time <= booking.end_time and end_time >= booking.start_time:
            return True
    return False


def booking_group_clashes_exists(start_date: date, end_date: date, start_time: time, end_time: time, recurring: str, venue: int) -> bool:
    clashes = BookingGroup.objects.filter(
            venue=venue,
            start_date__lte=end_date,
            end_date__gte=start_date,
            end_time__gt=start_time,
            start_time__lt=end_time,
            status='accepted',
        )
    if recurring == 'ALL':
        return clashes.exists()
    # If recurring is not ALL, then we need to check if there is a clash on the recurring day
    for clash in clashes:
        if clash.recurring == recurring or clash.recurring == 'ALL':
            return True
    return False


def get_pending_calendar_blocks(start_date: date, pending_bookings: QuerySet, accepted_bookings: QuerySet):
    pending_dict = {}
    pending_ret_list = []
    for i in range(7):
        pending_dict[str(start_date + td(days=i))] = [False for _ in range(24)]
    for booking in pending_bookings:
        end_hour = (booking.end_time.hour if booking.end_time.hour != 0 else 24)
        for i in range(booking.start_time.hour, end_hour):
            pending_dict[str(booking.date)][i] = True
    for booking in accepted_bookings:
        end_hour = (booking.end_time.hour if booking.end_time.hour != 0 else 24)
        for i in range(booking.start_time.hour, end_hour):
            pending_dict[str(booking.date)][i] = False
    for date, val in pending_dict.items():
        start_time = None
        for i in range(24):
            if not start_time and val[i] == True:
                start_time = f'{format(i, "02d")}:00:00'
            elif start_time and val[i] == False:
                pending_ret_list.append({
                    'date': date,
                    'start_time': start_time,
                    'end_time': f'{format(i, "02d")}:00:00'
                })
                start_time = None
    return pending_ret_list
