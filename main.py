#! /usr/local/bin/python3
from datetime import datetime,timedelta,date
import boto3
import logging
from config2 import *
import calendar
import sys

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
NOW = datetime.now()
MONTH_NAME = NOW.strftime('%B')
COUNT=0
#main process
for key in keys:
  COUNT=COUNT+1
  sts = boto3.client('sts',aws_access_key_id=key[0],aws_secret_access_key=key[1])
  #credential validation
  try:
    sts.get_caller_identity()
    ACCOUNT_ID = sts.get_caller_identity()["Account"]
    logging.info(" Credentials are valid for USER"+str(COUNT))
  except:
    logging.info(" Credentials invalid for USER"+str(COUNT)+" \nPlease Provide Valid Credentials in config file.\nThanks \n ")
    continue
    #sys.exit(0)

  #Taking Account_id from account
  sts = boto3.client('sts',aws_access_key_id=key[0],aws_secret_access_key=key[1])
  ACCOUNT_ID = sts.get_caller_identity()["Account"]

  #Taking Account_name from account
  #ACCOUNT_NAME =   boto3.client('organizations',aws_access_key_id=key[0],aws_secret_access_key=key[1]).describe_account(AccountId=ACCOUNT_ID).get('Account').get('Name')
  ACCOUNT_NAME = boto3.client('iam',aws_access_key_id=key[0],aws_secret_access_key=key[1]).list_account_aliases()['AccountAliases'][0]

  #Taking MonthToDate cost
  client1 = boto3.client('ce',aws_access_key_id=key[0],aws_secret_access_key=key[1])
  response1 = client1.get_cost_and_usage(TimePeriod={'Start': FIRST_DAY_DATE,'End': CURRENT_DAY_DATE},Granularity='MONTHLY',Metrics=['UNBLENDED_COST',],GroupBy=[{'Type': 'DIMENSION','Key': 'LINKED_ACCOUNT'},],)
  for groups in response1['ResultsByTime']:
    for amount in groups['Groups']:
      MONTH_TO_DATE_COST=str(amount['Metrics']['UnblendedCost']['Amount'])

  #Taking projection cost from forecast
  response2 = client1.get_cost_forecast(TimePeriod={'Start': TOMORROW_DAY_DATE,'End': LAST_DAY_DATE},Metric='UNBLENDED_COST',Granularity='MONTHLY',PredictionIntervalLevel=99)
  PROJECTION_COST=str(response2['Total']['Amount'])
  logging.info(str(MONTH_NAME)+" month to date cost for account "+str(ACCOUNT_NAME)+" ("+str(ACCOUNT_ID)+") is : $"+str(MONTH_TO_DATE_COST))
  logging.info(str(MONTH_NAME)+" month to date cost for account "+str(ACCOUNT_NAME)+" ("+str(ACCOUNT_ID)+") is : $"+str(PROJECTION_COST)+" \n  ")

