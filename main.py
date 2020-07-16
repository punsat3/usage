#! /usr/local/bin/python3
from datetime import datetime,timedelta,date
import boto3
import logging
from config2 import *
import calendar
import sys
from dateutil.relativedelta import relativedelta





#log file
logging.basicConfig(filename='elb.log', level=int(Level),
                    format='%(asctime)s:%(levelname)s:%(message)s',filemode='w')


#required Variables
CURRENT_DAY_DATE = str(datetime.today()).split()[0]
DATE_REPLACE = str(datetime.today().replace(day=1))
FIRST_DAY_DATE = DATE_REPLACE.split()[0]
LAST_DAY_DATE = str(date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1]))
DATE_ADDING = str(datetime.today() + timedelta(days=1))
TOMORROW_DAY_DATE = DATE_ADDING.split()[0]
NEXT_MONTH_FIRST_DATE = str(date.today().replace(day=1) + relativedelta(months=1))
NOW = datetime.now()
MONTH_NAME = NOW.strftime('%B')
COUNT=0
print (NEXT_MONTH_FIRST_DATE)
#main process
for key in keys:
  sts = boto3.client('sts')
  #credential validation
  try:
    sts.get_caller_identity()
    logging.info(" Credentials are valid for USER"+str(COUNT))
  except:
    logging.info(" Credentials invalid for USER"+str(COUNT)+" \nPlease Provide Valid Credentials in config file.\nThanks \n ")
    continue
    #sys.exit(0)

  #Taking MonthToDate cost

  client1 = boto3.client('ce')

  response1 = client1.get_cost_and_usage(TimePeriod={"Start": FIRST_DAY_DATE,"End": NEXT_MONTH_FIRST_DATE},Granularity='MONTHLY',Metrics=['UNBLENDED_COST',],GroupBy=[{'Type': 'DIMENSION','Key': 'LINKED_ACCOUNT'},],)
  for groups in response1['ResultsByTime']:
    for amount in groups['Groups']:
      MONTH_TO_DATE_COST=str(amount['Metrics']['UnblendedCost']['Amount'])
  print(MONTH_TO_DATE_COST)
  #Taking projection cost from forecast
  if TOMORROW_DAY_DATE==NEXT_MONTH_FIRST_DATE:
    logging.info(str(MONTH_NAME)+" Today is lastday of this month There is nothing predict cost. please check overall cost ")
    #response2 = client1.get_cost_forecast(TimePeriod={'Start': TOMORROW_DAY_DATE,'End': NEXT_MONTH_FIRST_DATE},Metric='UNBLENDED_COST',Granularity='MONTHLY',PredictionIntervalLevel=99)
  else:
    response2 = client1.get_cost_forecast(TimePeriod={'Start': TOMORROW_DAY_DATE,'End': NEXT_MONTH_FIRST_DATE},Metric='UNBLENDED_COST',Granularity='MONTHLY',PredictionIntervalLevel=99)
  PROJECTION_COST=str(response2['Total']['Amount'])
  logging.info(str(MONTH_NAME)+" month to date cost for account  is : $"+str(MONTH_TO_DATE_COST))
  logging.info(str(MONTH_NAME)+" months Projection cost for account is : $"+str(PROJECTION_COST)+" \n  ")
