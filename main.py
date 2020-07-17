from datetime import datetime,timedelta,date
import boto3
import logging
from config import *
import calendar
import sys
import os
from dateutil.relativedelta import relativedelta


logging.basicConfig(filename='elb.log', level=int(Level),
                    format='%(asctime)s:%(levelname)s:%(message)s',filemode='w')


if len(account_details)==0:
    logging.info("Please Provide at least one account details in config file")
    logging.debug("Please check account_details in config file")
    sys.exit(0)
for x in account_details:
    region="aws configure set default.region ap-south-1"
    profile="aws configure set profile." + x['Account_Name'] + ".role_arn arn:aws:iam::" + x['Account_ID'] + ":role/s3_cross_account"
    meta_data="aws configure set profile." + x['Account_Name'] + ".credential_source Ec2InstanceMetadata"
    os.system(region)
    os.system(profile)
    os.system(meta_data)
    print(region)
    print(profile)
    print(meta_data)
    session=boto3.Session(profile_name=x['Account_Name'])
    sts = session.client('sts')
    try:
        sts.get_caller_identity()
    except:
        logging.info(x['Account_Name']+ " Account invalid. Please configure IAM roles Properly for this account "+x['Account_ID'])
        print("")
        continue
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

    client1 = session.client('ce')

    response1 = client1.get_cost_and_usage(TimePeriod={"Start": FIRST_DAY_DATE,"End": NEXT_MONTH_FIRST_DATE},Granularity='MONTHLY',Metrics=['UNBLENDED_COST',],GroupBy=[{'Type': 'DIMENSION','Key': 'LINKED_ACCOUNT'},],)
    for groups in response1['ResultsByTime']:
        for amount in groups['Groups']:
          MONTH_TO_DATE_COST=str(amount['Metrics']['UnblendedCost']['Amount'])
    #Taking projection cost from forecast
    if TOMORROW_DAY_DATE==NEXT_MONTH_FIRST_DATE:
      logging.info(str(MONTH_NAME)+" Today is lastday of this month There is nothing predict cost. please check overall cost ")
        #response2 = client1.get_cost_forecast(TimePeriod={'Start': TOMORROW_DAY_DATE,'End': NEXT_MONTH_FIRST_DATE},Metric='UNBLENDED_COST',Granularity='MONTHLY',PredictionIntervalLevel=99)
    else:
      response2 = client1.get_cost_forecast(TimePeriod={'Start': TOMORROW_DAY_DATE,'End': NEXT_MONTH_FIRST_DATE},Metric='UNBLENDED_COST',Granularity='MONTHLY',PredictionIntervalLevel=99)
    PROJECTION_COST=str(response2['Total']['Amount'])
    logging.info("For account "+x['Account_ID']+" With Name "+x['Account_Name']+" :")
    logging.info("-----------------------------------------")
    logging.info(str(MONTH_NAME)+" month to date cost for account "+ x['Account_Name'] +" ("+x['Account_ID']+") is : $"+str(MONTH_TO_DATE_COST))
    logging.info(str(MONTH_NAME)+" months Projection cost for account "+ x['Account_Name'] +" ("+x['Account_ID']+") is : $"+str(PROJECTION_COST)+" \n  ")
