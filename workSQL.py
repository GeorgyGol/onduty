#!C:\Python33
# -*- coding: Cp1251 -*-

'''
Created on 21 окт. 2016 г.

@author: ggolyshev
'''
import pymssql
from datetime import datetime as DT
from datetime import date, timedelta
import FetchingHoly
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
cstrServer='L26-SRV0'
cstrDB='CMASFPersonal'
cstrDBUser=r'cmasf\mls'
cstrDBUserPass='222222'
cstrSendMailUser='MElizarova@forecast.ru'
cstrSendMailUserPass='Cmakp1302'
cstrSendMailTo='g.golyshev@forecast.ru'

tstrSendMailText='Сегодня в 1302 дежурит {0}'

tblPers='Personal'
tblDuty='DateTable'
tblHoly='Selebrates'

ONE_DAY=timedelta(days=1)
ONE_MONTH=timedelta(weeks=5)

NEXT_MONTH=FetchingHoly.nextMonth(DT.today()).date()
CURR_MONTH=FetchingHoly.firstDay(DT.today())
PREV_MONTH=FetchingHoly.prevMonth(DT.today()) 

class lstUsers(list):
    _iCurrent=0
    
    def __init__(self, lst=None, **kwargs):
        if lst:
            super().__init__(lst)
        else:
            super().__init__()
        if kwargs:
            super().__init__(kwargs)
    
    def __getitem__(self, i):
        k=None
        try:
            k=list.__getitem__(self, i)
            self._iCurrent=i
        except IndexError:
            self._iCurrent=0
            k= list.__getitem__(self, 0)
        return k    

    @property
    def Current(self):
        return self._iCurrent
    
    @Current.setter
    def Current(self, Index):
        self._iCurrent=Index
    
    def Find(self, findWhat):
        if findWhat==-1:return -1
        for indx, item in enumerate(self):
            if item['id']==findWhat:
                return indx
    
class sqlOnDuty():
    _conn=None
    _strDBName=''
    _users=lstUsers()
    
    def __init__(self, str_server='', str_user=r'',
                str_password="", str_database=''):
        
        self._strDBName=str_database
        try:
            self._conn=pymssql.connect(host=str_server, user=str_user, 
                            password=str_password, database=str_database)
        except pymssql.OperationalError:
            print('Program terminated, connection failed - check user name and pass')
            exit()
        except pymssql.InterfaceError:
            print('Program terminated, connection failed - check server name')
            exit()
        
    def __del__(self):
        try:
            self._conn.close()
        except:
            pass

    def writeHolidays(self, to_year):
        s_d='''DELETE FROM {0} WHERE YEAR([MDate])={1}'''.format(tblHoly, to_year)
        clF=FetchingHoly.clsHolyInfo(to_year)
        list_parm=list()
        for x in clF:
            for d in x['date']:
                list_parm.append((d, x['title']))
        
        curs=self._conn.cursor()
        curs.execute(s_d)
        s_i='''INSERT INTO {0} VALUES (%d, %s)'''.format(tblHoly)
        curs.executemany(s_i, list_parm)
        self._conn.commit()
    
    def Holydays(self, to_year):
        s='''SELECT MDate, Selebinfo from dbo.{0} where Year(MDate)={1}'''.format(tblHoly, to_year)
        curs=self._conn.cursor()
        curs.execute(s)
        return { DT.date(row[0]) for row in curs }
            
    def Users(self):
        cursor=self._conn.cursor(as_dict=True)
        cursor.execute('SELECT SCode as id, LogName, SName, SFName, Family FROM dbo.{0} WHERE isWD <> 0 ORDER BY Family'.format(tblPers))
        for row in cursor:
            self._users.append(dict(row))
        return self._users
    
    def DutyDate(self, date_from=DT.today().date(), 
                 date_to=None):
        cursor=self._conn.cursor(as_dict=True)
        
        s1='''SELECT ID as id, Family, MDate as date 
        FROM dbo.{0} WHERE (MDate >= '{1}') ORDER BY MDate'''.format(tblDuty, date_from)
        
        s2='''SELECT ID as id, Family, MDate as date 
        FROM dbo.{0} WHERE (MDate >= '{1}') and (MDate < '{2}') 
        ORDER BY MDate'''.format(tblDuty, date_from, date_to)
        
        #print (s2)
        if date_to is None:
            cursor.execute(s1)
        else:
            cursor.execute(s2)

        return [row for row in cursor]
    
    def getCurrentDuty(self, dtWhat):
        s2='''SELECT ID as id, Family, MDate as date 
        FROM dbo.{0} WHERE (MDate = '{1}')'''.format(tblDuty, dtWhat.date())
        #print (s2)
        cursor=self._conn.cursor(as_dict=True)
        cursor.execute(s2)
        return cursor.fetchone()

    
    def LastDutyID(self, forDate):
        dtt=FetchingHoly.firstDay(forDate)
        try:
            return self.DutyDate(dtt, FetchingHoly.nextMonth(dtt))[-1]['id']
        except IndexError:
            return -1
    
    def writeDuty(self, dtTo, lstParams):
        firstDT=FetchingHoly.firstDay(dtTo)
        lastDT=FetchingHoly.nextMonth(firstDT)
        s_d='''DELETE FROM {0} WHERE ([MDate]>='{1}') AND ([MDate]< '{2}')'''.format(tblDuty, firstDT, lastDT)
        
        cursor=self._conn.cursor()
        cursor.execute(s_d)
        self._conn.commit()
        
        s_i='''INSERT INTO {0} VALUES (%d, %s, %d)'''.format(tblDuty)
        #print(s_i)
        #print(lstParams)
        cursor.executemany(s_i, lstParams)
        self._conn.commit()

#c.writeHolidays(2017)

#print (c.LastDutyID(DT(2017, 2, 1)))
def writeHollydays(iYear):
    c=sqlOnDuty(cstrServer, str_user=cstrDBUser, 
        str_password=cstrDBUserPass, str_database=cstrDB)
    c.writeHolidays(iYear)
    print ('Writed hollydays onto DB.')

def sendDutyMail():
    c=sqlOnDuty(cstrServer, str_user=cstrDBUser, 
        str_password=cstrDBUserPass, str_database=cstrDB)
    cd=(c.getCurrentDuty(DT.today()))

    from_addr=cstrSendMailUser
    to_addr=cstrSendMailTo
    mp=cstrSendMailUserPass

    body=tstrSendMailText.format(cd['Family'].upper())

    msg=MIMEText(body)
    msg['From']=from_addr
    msg['To']=to_addr
    msg['Subject'] = 'Дежурство на ' + DT.strftime(DT.today(), '%d.%m.%Y') 

    msg['X-Priority']='1 (Highest)'
    text=msg.as_string()

    serv=smtplib.SMTP('smtp.gmail.com', 587)
    serv.starttls()
    serv.login(from_addr, mp)

    serv.sendmail(from_addr, to_addr, text) 
    serv.quit()
    print('Done sending email message.')

def MakeDuty(dtForWhat, lStartFromID=0):
    c=sqlOnDuty(cstrServer, str_user=cstrDBUser, 
        str_password=cstrDBUserPass, str_database=cstrDB)
    u=c.Users()
    #print (c.LastDutyID(DT.today()))
    dtt=FetchingHoly.firstDay(dtForWhat)
    sHoly=c.Holydays(dtForWhat.year)
    if not sHoly:
        c.writeHolidays(dtForWhat.year)
        sHoly=c.Holydays(dtForWhat.year)
        
    res_st=FetchingHoly.workingDaysByCalendar(dtt, FetchingHoly.nextMonth(dtt))-sHoly
    lst_date=sorted(list(res_st))
    if not lStartFromID:
        lastID=c.LastDutyID(FetchingHoly.prevMonth(dtForWhat))
        u.Current=u.Find(lastID)+1
    else:
        u.Current=u.Find(lStartFromID)

    lst_parm=[]
    for k in lst_date:
        lst_parm.append((u[u.Current]['id'], u[u.Current]['Family'], k))
        u.Current+=1
        
    c.writeDuty(dtForWhat, lst_parm)
    print('Done writing duty table.')
    #print (lst_parm)
    
#MakeDuty(DT(2017, 1, 1))
                   
#MakeDuty(DT.today())
#c.DutyDate(date_from=date(DT.today().year, DT.today().month-1, 1), 
#           date_to=date(2016, 11, 1))

#d=DT.today().date(87)
#d1=d+2*ONE_MONTH
#print (d, d1)