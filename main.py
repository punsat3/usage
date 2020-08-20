import sys
from datetime import datetime,timedelta,date
import boto3
import logging
from Config import *
import calendar
import os
from botocore.exceptions import ClientError
from dateutil.relativedelta import relativedelta

WEEKNUMBER = date.today().isocalendar()[1]
TODAY_DATE_FULL=datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
logging.basicConfig(filename='Cost_Explorer_'+str(TODAY_DATE_FULL)+'.log', level=int(Level),
                    format='%(asctime)s:%(levelname)s:%(message)s',filemode='w')

FILENAME="Airtel_Streaming_AWS_Billing_Report_"+str(TODAY_DATE_FULL)+".report"
f = open(FILENAME, "w")

#checking whether account_details
if len(account_details)==0:
    logging.info(+str(sys.argv[0])+"Please Provide at least one account details in config file")
    sys.exit(0)

# loop is goingon in account_details
for x in account_details:
    #try to set profile withRole arn
    try:
        region="aws configure set default.region us-west-2"
        profile="aws configure set profile." + x['Account_Name'] + ".role_arn arn:aws:iam::" + x['Account_ID'] + ":role/"+x['role']
        meta_data="aws configure set profile." + x['Account_Name'] + ".credential_source Ec2InstanceMetadata"
        os.system(region)
        os.system(profile)
        os.system(meta_data)
        session=boto3.Session(profile_name=x['Account_Name'])
        sts = session.client('sts')
        sts.get_caller_identity()
        logging.info(str(sys.argv[0])+" : "+x['Account_Name']+" : "+x['Account_ID']+" account has valid role and successfully login with role  in account  ")
    except ClientError as e:
        logging.warning(str(sys.argv[0])+" : "+x['Account_Name']+" : "+x['Account_ID']+" account has invalid Role. Please configure proper IAM roles and now we are trying with  access keys for this account ")
        logging.debug(str(sys.argv[0])+" : "+x['Account_Name']+" : "+x['Account_ID']+" account has invalid Role. Please configure proper IAM role and policies in account ")
        try:
            if e.response['Error']['Code'] == 'AccessDenied':
                session=boto3.Session(aws_access_key_id=x['access_key'],aws_secret_access_key=x['secret_access_key'])
                sts = session.client('sts')
                sts.get_caller_identity()
                logging.info(str(sys.argv[0])+" : "+x['Account_Name']+" : "+x['Account_ID']+" account has valid accesskey and secret-accesskey and successfully login   in account ")
        except:
            logging.info(str(sys.argv[0])+" : "+x['Account_Name']+" : "+x['Account_ID']+" account has invalid Details. Please configure proper IAM roles or access keys for this account ")
            continue
    #required Variables
    FIRST_DAY_DATE = str(date.today().replace(day=1))
    TOMORROW_DAY_DATE = str(date.today() + timedelta(days=1))
    NEXT_MONTH_FIRST_DATE = str(date.today().replace(day=1) + relativedelta(months=1))
    NOW = datetime.now()
    MONTH_NAME = NOW.strftime('%B')
    LAST_DAY_OF_CURRENT_MONTH=calendar.monthrange(date.today().year,date.today().month)[1]
    TODAY_DATE_IN_DAY=date.today().day
    digits=2
    TODAY_DATE_FULL=str(date.today())

    ce_client = session.client('ce')

    cost_usage_response = ce_client.get_cost_and_usage(TimePeriod={"Start": FIRST_DAY_DATE,"End": NEXT_MONTH_FIRST_DATE},Granularity='MONTHLY',Metrics=['UNBLENDED_COST',],GroupBy=[{'Type': 'DIMENSION','Key': 'LINKED_ACCOUNT'},],)
    for groups in cost_usage_response['ResultsByTime']:
        for amount in groups['Groups']:
          fnum1=str(amount['Metrics']['UnblendedCost']['Amount'])
          MONTH_TO_DATE_COST = float(fnum1[:fnum1.find('.') + digits + 1])

        logging.info(str(sys.argv[0])+" : "+x['Account_Name']+" : "+x['Account_ID']+" For account "+x['Account_ID']+" With Name "+x['Account_Name']+" :")
        logging.info("-----------------------------------------")
        logging.info(str(sys.argv[0])+" : "+str(MONTH_NAME)+" month to date cost for account "+ x['Account_Name'] +" ("+x['Account_ID']+") is : $"+str(MONTH_TO_DATE_COST))
        f.write(str(MONTH_NAME)+" month to date cost for account "+ x['Account_Name'] +" ("+x['Account_ID']+") is : $"+str(MONTH_TO_DATE_COST)+" \n")

#Taking projection cost from forecast

    if TODAY_DATE_IN_DAY == LAST_DAY_OF_CURRENT_MONTH:
        logging.info(str(sys.argv[0])+" : "+str(MONTH_NAME)+" months Projection cost for account "+ x['Account_Name'] +" ("+x['Account_ID']+") is : $"+str(MONTH_TO_DATE_COST)+" \n")
        f.write(str(MONTH_NAME)+" months Projection cost for account "+ x['Account_Name'] +" ("+x['Account_ID']+") is : $"+str(MONTH_TO_DATE_COST)+" \n")
        f.write("\n")
    else:
        forecast_response = ce_client.get_cost_forecast(TimePeriod={'Start': TOMORROW_DAY_DATE,'End': NEXT_MONTH_FIRST_DATE},Metric='BLENDED_COST',Granularity='MONTHLY',PredictionIntervalLevel=99)
        fnum2=str(forecast_response['Total']['Amount'])
        PROJECTION_COST = float(fnum2[:fnum2.find('.') + digits + 1])
        logging.info(str(sys.argv[0])+" : "+str(MONTH_NAME)+" months Projection cost for account "+ x['Account_Name'] +" ("+x['Account_ID']+") is : $"+str(PROJECTION_COST)+" \n")
        f.write(str(MONTH_NAME)+" months Projection cost for account "+ x['Account_Name'] +" ("+x['Account_ID']+") is : $"+str(PROJECTION_COST)+" \n")
        f.write("\n")

f.close()
#copy="aws s3 cp "+str(FILENAME)+" "+s3_bucket
#os.system(copy)
f = open(FILENAME, "r")
report=f.read()
remove="rm "+str(FILENAME)
os.system(remove)
print("done")

