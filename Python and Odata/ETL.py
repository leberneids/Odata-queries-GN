# import needed libraries
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from sqlalchemy import create_engine
import os
from sqlalchemy.engine import URL

# get password from environment variable
pwd = os.environ['PGPASS']
uid = os.environ['PGUID']

server = "localhost"
database = "Devops;"

content = open('config/config.json')
config = json.load(content)

user = config['user']
password = config['password']


# extract data from Azure DevOps using OData and use the config file 
def extract():
    try:
        url = "https://analytics.dev.azure.com/GNHearing/_odata/v3.0/WorkItems?%24filter=+%28WorkItemType+eq+%27Epic%27%29+and+Project%2FProjectName+eq+%27GNH%27+and+Parent%2FWorkItemId+ne+null+and+Parent%2FArea%2FAreaPath+eq+%27GNH%27+and+Parent%2FWorkItemType+eq+%27Portfolio+Epic%27+and+State+ne+%27Closed%27+and+State+ne+%27Removed%27+and+Parent%2FState+ne+%27Closed%27+and+Parent%2FState+ne+%27Removed%27+or+%28WorkItemType+eq+%27Epics%27%29+and+Project%2FProjectName+eq+%27GNH%27+and+Parent%2FParent%2FWorkItemId+ne+null+and+Parent%2FParent%2FArea%2FAreaPath+eq+%27GNH%27+and+Parent%2FParent%2FWorkItemType+eq+%27Portfolio+Epic%27+and+State+ne+%27Closed%27+and+State+ne+%27Removed%27+and+Parent%2FState+ne+%27Closed%27+and+Parent%2FState+ne+%27Removed%27+and+Parent%2FParent%2FState+ne+%27Closed%27+and+Parent%2FParent%2FState+ne+%27Removed%27&%24select=WorkItemId%2C+WorkItemType%2C+Title%2C+State%2CGNH_ValueType%2C+Custom_D1Planned%2C+Custom_D3Planned%2C+Custom_D2Planned%2C+Custom_Heartbeat%2C+TagNames%2C+Custom_TimeRegistrationID%2C+BusinessValue"
        response = requests.get(url, auth=HTTPBasicAuth(user, password))
        data = response.json()
        df = pd.json_normalize(data['value'])
        tbl_name = "FirstTable"
        return df, tbl_name
    except Exception as e:
        print("Data extract error: " + str(e))

# load data to PostgreSQL
def load(df, tbl):
    try:
        rows_imported = 0
        engine = create_engine(f'postgresql://{uid}:{pwd}@localhost:5432/Devops')
        print(f'importing rows {rows_imported} to {rows_imported + len(df)}... for table {tbl}')
        # save df to PostgreSQL
        df.to_sql(f'stg_{tbl}', engine, if_exists='replace', index=False)
        rows_imported += len(df)
        # add elapsed time to final print out
        print("Data imported successfully")
    except Exception as e:
        print("Data load error: " + str(e))

# execute ETL process
df, tbl_name = extract()
load(df, tbl_name)
