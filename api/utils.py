import datetime


def adjust_to_facility_day(date, facility):
    """
    Given a scheduled date, move it to the nearest facility vaccination day.
    If facility has no fixed days, return the original date.
    """
    days = list(facility.vaccination_days.values_list("day_of_week", flat=True))
    if not days:
        return date  # no restriction, keep original date

    # If exact match, return
    if date.weekday() in days:
        return date

    # Find nearest upcoming vaccination day
    for i in range(1, 8):
        candidate = date + datetime.timedelta(days=i)
        if candidate.weekday() in days:
            return candidate
    return date  # fallback
