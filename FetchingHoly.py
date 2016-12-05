#!C:\Python33
# -*- coding: Cp1251 -*-
'''
Created on 14 нояб. 2016 г.

@author: golyshev
'''

import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime as CONV_DT
from datetime import date, timedelta

serv_url=r'http://xmlcalendar.ru/data/ru/{0}/calendar.xml'

class clsHolyInfo():
    _dctHld=list()
    _dt_source=None
    
    def __init__(self, s_year):
        uh = urllib.request.urlopen(serv_url.format(s_year))
        root=ET.fromstring(uh.read())
        if root.tag != 'calendar' or root.attrib['year'] != str(s_year):
            raise Exception('wrong site or wrong year in input data')
            exit()

        self.__dt_source=CONV_DT.strptime(root.attrib['date'], "%Y.%m.%d")

        for hldd in root.iter('holiday'):
            k=[date(s_year,  int(x.attrib['d'][:2]), int(x.attrib['d'][-2:])) 
                for x in root.iter('day') if x.attrib['t']=='1' and x.attrib.get('h', 0)==hldd.attrib['id']]

            hldd.attrib.pop('id')
            hldd.attrib.setdefault('date', k)
            self._dctHld.append(hldd.attrib)
            
    def __repr__(self):
        return self._dctHld
    
    def __str__(self):
        return str(self._dctHld)
    
    def __iter__(self):
        for x in self._dctHld:
            yield x
    
    @property
    def sourceDate(self): 
        return  self.__dt_source.date()

class clsHolyDays():
    _holydays=frozenset()
    _dt_source=None
    
    def DateConvert(self, y, s):
        return date(y, int(s[:2]), int(s[-2:])) 
    
    def __init__(self, s_year):
        uh = urllib.request.urlopen(serv_url.format(s_year))
        root=ET.fromstring(uh.read())
        if root.tag != 'calendar' or root.attrib['year'] != str(s_year):
            raise Exception('wrong site or wrong year in input data')
            exit()
        self.__dt_source=CONV_DT.strptime(root.attrib['date'], "%Y.%m.%d")

        self._holydays={self.DateConvert(s_year, x.attrib['d']) 
                for x in root.iter('day') if x.attrib['t']=='1'}

    def __repr__(self):
        return self._holydays
    
    def __str__(self):
        return str(self._holydays)

    @property
    def sourceDate(self): 
        return  self.__dt_source.date()
 
    def __iter__(self):
        for x in self._holydays:
            yield x
 
 
def workingDaysByCalendar(date_from, date_to):
    td=timedelta(days=1)
    ls=set()
    dt_cur=date_from
    while dt_cur != date_to:
        #print ('cur-day ' + str(dt_cur.day))
        #print ('week-day ' + str(dt_cur.weekday()))
        if dt_cur.weekday() not in (5, 6): 
            ls.add(dt_cur)
        dt_cur+=td
    return ls

def nextMonth(dtFromDate):
    delta=timedelta(weeks=5)
    return (dtFromDate.replace(day=1)+delta).replace(day=1)

def firstDay(dtFromDate):
    #print(dtFromDate, dtFromDate.replace(day=1).date())
    try:
        return dtFromDate.replace(day=1).date()
    except AttributeError:
        return dtFromDate.replace(day=1)

def prevMonth(dtWhat):
    return firstDay(firstDay(dtWhat)-timedelta(days=1))
#c=clsHolyDays(2017)
#print(c.sourceDate)

#print(prevMonth(CONV_DT(2017, 1, 1)))
                
'''  
print (workingDaysByCalendar(date(2016, 10, 1), date(2016, 12, 1)))
lst=sorted(list( workingDaysByCalendar(date(2016, 10, 1), date(2016, 12, 1))))
for x in lst:
    print(x)
    
print ('Next - ', nextMonth(date(2016, 11, 30)))  
 
 
d=clsHolyDays(2017)
print(set(d))

ds={date(2017, 1, i) for i in range(1, 31)}
print (ds)

print (sorted(list(ds - set(d))))
'''