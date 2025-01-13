from datetime import datetime

from frx.settings import WORKING_HOURS_START, WORKING_HOURS_END, WORKING_WEEK_DAYS_START, WORKING_WEEK_DAYS_END


def working_hours():
    if not (int(WORKING_WEEK_DAYS_START) <= datetime.now().weekday() + 1 <= int(WORKING_WEEK_DAYS_END)):
        return False

    if int(WORKING_HOURS_START) <= datetime.now().hour < int(WORKING_HOURS_END):
        return True

    return False
