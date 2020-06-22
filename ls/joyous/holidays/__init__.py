# ------------------------------------------------------------------------------
# Joyous Holidays
# ------------------------------------------------------------------------------
import datetime as dt
from collections import OrderedDict
from django.conf import settings
from .parser import parseHolidays

class Holidays:
    """Defines what holidays are celebrated on what dates."""
    def __init__(self, holidaySetting="JOYOUS_HOLIDAYS"):
        self.setting = holidaySetting
        self.simple = {}
        self.srcs = [ self.simple ]
        self._parseSettings()

    def _parseSettings(self):
        if self.setting:
            holidaySettings = getattr(settings, self.setting, "")
            if holidaySettings:
                hols = parseHolidays(holidaySettings)
                if hols is not None:
                    self.register(hols)

    def register(self, src):
        """Register a new source of holiday data."""
        self.srcs.append(src)

    def add(self, date, value):
        """Add a holiday to an individual date."""
        oldValue = self.simple.get(date)
        if oldValue:
            if oldValue not in value and value not in oldValue:
                self.simple[date] = "{}, {}".format(oldValue, value)
        else:
            self.simple[date] = value

    def get(self, date):
        """Get all the holidays that are celebrated on this date."""
        holidays = []
        for src in self.srcs:
            # get from python-holidays and other dict type srcs
            getHoliday = getattr(src, "get", None)
            if not getHoliday:
                # get from workalendar srcs
                getHoliday = getattr(src, "get_holiday_label")
            holiday = getHoliday(date)
            if holiday:
                holidays.extend(holiday.split(", "))
        holidays = list(OrderedDict.fromkeys(holidays))   # remove duplicates
        return ", ".join(holidays)

    def names(self):
        """Get a list of all the holiday names, sorted by month-day."""
        thisYear = dt.date.today().year
        popYears = list(range(thisYear + 10, thisYear + 1, -1))
        popYears.append(thisYear - 1)
        popYears.append(thisYear + 1)
        popYears.append(thisYear)

        holidays = {}
        for src in self.srcs:
            # populate python-holidays calendar
            populate = getattr(src, "_populate", None)
            if populate:
                for year in popYears:
                    populate(year)

            # get from python-holidays and other dict type srcs
            items = getattr(src, "items", None)
            if items:
                for date, names in items():
                    # holidays may have been concatenated together
                    for name in names.split(", "):
                        holidays[name] = (date.month, date.day)
            else:
                # get from workalendar srcs
                getHolidays = getattr(src, "get_calendar_holidays", None)
                if getHolidays:
                    for year in popYears:
                        for date, name in getHolidays(year):
                            holidays[name] = (date.month, date.day)
        mmddHolidays = [(mmdd, name) for name, mmdd in holidays.items()]
        mmddHolidays.sort()
        retval = [name for mmdd, name in mmddHolidays]
        return retval

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
