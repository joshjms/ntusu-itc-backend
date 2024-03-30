from datetime import datetime as dt
from typing import Iterable
from ulocker.models import Booking, Locker


'''
Utility class that provides methods to get the status of lockers.
Simply call LockerStatusUtils.get_locker_status,
passing as arguments a queryset of lockers, start_month and duration.
The 'status' field will be annotated to each locker in the queryset.

Status is determined based on the following priority:
- If Locker.is_available is False, status is 'not available'.
- If there is at least one booking that overlaps with the given start_month and duration,
and the booking status is 'allocated', status is 'occupied'.
- If there is at least one booking that overlaps with the given start_month and duration,
and the booking status is 'pending', 'awaiting payment' or 'awaiting verification',
status is 'reserved'.
- Otherwise, status is 'available'.
'''
class LockerStatusUtils:
    STATUS_PRIORITY_MAP = {
        0: 'available',
        1: 'reserved',
        2: 'occupied',
        3: 'not available'
    }
    
    @staticmethod
    def get_locker_status(queryset: Iterable[Locker],
                          start_month: int=None,
                          duration: int=1) -> Iterable[Locker]:
        if start_month is None:
            start_month = dt.now().strftime('%m/%Y')
        bookings = Booking.objects.all()
        
        for locker in queryset:
            if locker.is_available == False:
                locker.status = LockerStatusUtils.STATUS_PRIORITY_MAP[3]
                continue
            
            status_number = 0
            for booking in bookings:
                if LockerStatusUtils.check_overlap(booking.start_month, booking.duration, start_month, duration):
                    if booking.status in ['allocated']:
                        status_number = max(status_number, 2)
                    elif booking.status in ['pending', 'approved - awaiting payment', 'approved - awaiting verification']:
                        status_number = max(status_number, 1)
                    else:
                        status_number = max(status_number, 0)
                        
            locker.status = LockerStatusUtils.STATUS_PRIORITY_MAP[status_number]
        return queryset
    
    @staticmethod         
    def calculate_end_month(start_month, duration):
        start_month = start_month.split('/')
        month = int(start_month[0])
        year = int(start_month[1])
        duration = int(duration)
        month += duration - 1
        while month > 12:
            month -= 12
            year += 1
        return f'{month:02d}/{year}'

    @staticmethod
    def check_overlap(start_month1, duration1, start_month2, duration2):
        end_month1 = LockerStatusUtils.calculate_end_month(start_month1, duration1)
        end_month2 = LockerStatusUtils.calculate_end_month(start_month2, duration2)
        if start_month1 == start_month2 or end_month1 == end_month2:
            return True
        if start_month1 < start_month2:
            return end_month1 >= start_month2
        else:
            return end_month2 >= start_month1
