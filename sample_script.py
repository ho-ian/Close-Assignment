import close
from closeio_api import APIError, Client
import pandas as pd
import re
import time
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description='Close API posting contacts and leads.')
args = parser.parse_args()

# grabbing csv file and reading it into a pandas dataframe
# https://stackoverflow.com/a/50377166 was particularly helpful
url = "https://docs.google.com/spreadsheets/d/1omg1_ZSCMlTLzwv9tON7pkGU10_rDOeJeKmTi_qtf-k/edit#gid=1081785221"
csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=')
csv = pd.read_csv(csv_url)

### PART a ###

# will want to post all leads first and then add contacts afterwards
# posting leads will generate unique lead id's for each lead which we will match up to each contact later
leads_pd = csv[['Company', 'custom.Company Founded', 'custom.Company Revenue', 'Company US State']]
leads_pd = leads_pd.drop_duplicates()
leads_pd = leads_pd.fillna('')

# change object type of company founded to date and revenue to float
leads_pd['date'] = leads_pd['custom.Company Founded'].apply(close.convertDate)
leads_pd['revenue'] = leads_pd['custom.Company Revenue'].apply(close.convertFloat)

# contacts will need to be identified by company, name, email and phone numbers
contacts_pd = csv[['Company', 'Contact Name', 'Contact Emails', 'Contact Phones']]
contacts_pd = contacts_pd.fillna('')

# parse and post all leads
leads_pd['json'] = leads_pd.apply(close.leadParse, axis=1)
leads_pd['json'].apply(close.postLead)
time.sleep(7)
# we set a wait timer for 7 seconds just to make sure all leads are posted before we get the leads and their respective lead ids

# getting rid of invalid data
contacts_pd['Contact Phones'] = contacts_pd['Contact Phones'].apply(close.validateNumber)
contacts_pd['Contact Emails'] = contacts_pd['Contact Emails'].apply(close.validateEmail)

#grabbing leads so we can get lead id's and match them when we post our contacts
lead_results = close.getLeads()

lead_data = lead_results["data"]
lead_data = pd.json_normalize(lead_data)
lead_data = lead_data.rename(columns={"display_name":"Company"})

contacts_pd = contacts_pd.merge(lead_data, on="Company")

# parse and post all contacts
contacts_pd['json'] = contacts_pd.apply(close.contactParse, axis=1)
contacts_pd['json'].apply(close.postContact)


### PART b ###

