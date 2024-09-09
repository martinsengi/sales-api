from datetime import datetime, time, timezone

from django.utils import timezone as django_timezone


def convert_date_to_utc(date: datetime, is_end_of_day: bool = False) -> datetime:
    if is_end_of_day:
        date_time = datetime.combine(date, time.max)
    else:
        date_time = datetime.combine(date, time.min)

    aware_datetime = django_timezone.make_aware(date_time, django_timezone.get_current_timezone())

    return django_timezone.localtime(aware_datetime, timezone.utc)
