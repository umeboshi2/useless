#import os, sys
import calendar

from useless.webframe.forgethtml import Table, TableRow
from useless.webframe.forgethtml import TableCell, TableHeader

calendar.setfirstweekday(calendar.SUNDAY)

class BaseCalendar(Table):
    def __init__(self, month, year, **args):
        Table.__init__(self, **args)
        self.month = month
        self.year = year
        self.make_calendar()
        
    def make_calendar(self):
        self.clear()
        self.append(self.make_monthheader())
        self.append(self.make_weekheader())
        for week in calendar.monthcalendar(self.year, self.month):
            self.append(self.make_week(week))
                
    def make_monthheader(self):
        return TableHeader(calendar.month_name[self.month], colspan=8)
        
    def make_weekheader(self):
        row = TableRow()
        for day in calendar.weekheader(3).split():
            td = TableCell(day)
            row.append(td)
        return row
    
    def make_week(self, week):
        weekrow = TableRow()
        for day in week:
            daycell = self.make_day(week, day)
            weekrow.append(daycell)
        return weekrow            

    def append_week(self, week):
        self.append(weekrow)


    def make_day(self, week, day):
        if day:
            td = TableCell(str(day))
        else:
            td = TableCell()
        return td
    
