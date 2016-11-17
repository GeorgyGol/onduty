#!/usr/local/bin/python2.7
# encoding: utf-8
'''
onduty -- shortdesc

onduty is a description

It defines classes_and_methods

@author:     G. Golyshev

@copyright:  2016 CMASF. All rights reserved.

@license:    license

@contact:    G.Golyshev@gmail.com
@deffield    updated: Updated
'''

import argparse
from workSQL import MakeDuty, sendDutyMail, writeHollydays
from workSQL import NEXT_MONTH, CURR_MONTH, PREV_MONTH
from datetime import date

__all__ = []
__version__ = 0.1

DEBUG = 1
TESTRUN = 0
PROFILE = 0

def createParser():
    parser= argparse.ArgumentParser(prog='onduty', description='''Расчет дежурных по Центру. Обновляет таблицу DateTable
    в базе данных ЦМАКП, либо в автоматическом режиме (продление), либо на указанный месяц.
    Можно указать ID стартового дежурного месяца. Так же программа рассылает email-сообщение о текущем дежурном и
    обновляет таблицу с нерабочими днями на указанный год.''', 
    epilog='''(c) ЦМАКП, ноябрь 2016. Автор: golyshev  ''')
    
    parser.add_argument('-d', '--data', help='''Любая дата из расчитываемого периода 
    (расчитывается график на месяц). Формат даты - dd.mm.yyyy''')
   
    parser.add_argument('-u', '--user', help='''ID стартового дежурного (см. в базе данных)''', type=int)

    parser.add_argument('-m', '-send_mail', help='''Рассылка email-сообщения о текущем дежурном. Если этот параметр установлен, остальные игнорируются''',
                        action='store_true', default=False,)
    
    parser.add_argument('-y', '--year_hollydays', type=int,
                           help='''Установка нерабочих дней на указанный год (данные беруться из Сети), 
                           если этот параметр установлен, другие игнорируются''')
    
    return parser

if __name__ == '__main__':
    parser=createParser()
    ns=parser.parse_args()
    print(ns)
    if ns.m:
        sendDutyMail()
    elif ns.year_hollydays:
        writeHollydays(ns.year_hollydays)
    else:
        dt=date(int(ns.data[-4:]), int(ns.data[3:5]), int(ns.data[:2])) if ns.data !=None else NEXT_MONTH
        uid=0 if ns.user==None else ns.user
        #print (dt, uid)
        MakeDuty(dt, uid)
        #print (NEXT_MONTH, CURR_MONTH, PREV_MONTH)