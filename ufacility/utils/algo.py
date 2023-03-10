from ufacility.models import Booking2, BookingGroup


def clash_exists(venue, date, start_time, end_time):
    bookings = Booking2.objects.filter(venue=venue, date=date)
    for booking in bookings:
        if start_time <= booking.end_time and end_time >= booking.start_time:
            return True
    return False


def get_booking_group_clashes(BookingGroup: BookingGroup):
    pass
    '''
        TODO
        Given a BookingGroup instance, determine clash or not.
    '''
