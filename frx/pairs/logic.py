from datetime import datetime

from frx.settings import WORKING_HOURS_START, WORKING_HOURS_END


def working_hours():
    if int(WORKING_HOURS_START) <= datetime.now().hour < int(WORKING_HOURS_END):
        return True
    return False
