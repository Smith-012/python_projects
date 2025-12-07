import calendar
from datetime import datetime

def get_tuesdays_fridays(year: int, month: int):
    """
    Returns all Tuesday and Friday dates for the given month & year.
    """
    cal = calendar.Calendar()
    tuesdays = []
    fridays = []

    for day in cal.itermonthdates(year, month):
        if day.month == month:  # ensure it's within the given month
            if day.weekday() == 1:  # Tuesday = 1
                tuesdays.append(day.day)
            elif day.weekday() == 4:  # Friday = 4
                fridays.append(day.day)

    return tuesdays, fridays


# Example usage:
year = int(input("Enter year: "))
month = int(input("Enter month (1-12): "))

tues, fris = get_tuesdays_fridays(year, month)

print("Tuesdays:", tues)
print("Fridays:", fris)
