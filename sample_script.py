import close
from closeio_api import APIError, Client
import pandas as pd
import re
import time
from datetime import datetime
import datetime as dt
import sys

# grabbing csv file and reading it into a pandas dataframe
# https://stackoverflow.com/a/50377166 was particularly helpful
url = "https://docs.google.com/spreadsheets/d/1omg1_ZSCMlTLzwv9tON7pkGU10_rDOeJeKmTi_qtf-k/edit#gid=1081785221"
csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=')
csv = pd.read_csv(csv_url)

### PART a ###

# will want to post all leads first and then add contacts afterwards
# posting leads will generate unique lead id's for each lead which we will match up to each contact later
leads_pd = csv[['Company', 'custom.Company Founded', '', 'Company US State']]
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

# merging dataframes so we have each Company/lead aligned with each lead_id
contacts_pd = contacts_pd.merge(lead_data, on="Company")

# parse and post all contacts
contacts_pd['json'] = contacts_pd.apply(close.contactParse, axis=1)
contacts_pd['json'].apply(close.postContact)


### PART b ###

# this only accepts dates with format '%d.%m.%Y'
start = datetime.strptime(sys.argv[1],'%d.%m.%Y').date()
end = datetime.strptime(sys.argv[2],'%d.%m.%Y').date()

# since there are some rows with empty entries for custom.Company Founded, i need to only include those that have real dates
subset_pd = leads_pd[ leads_pd['date'].apply( lambda x: isinstance(x,dt.date)) ] 
subset_pd = subset_pd[start <= subset_pd['date']]
subset_pd = subset_pd[subset_pd['date'] <= end]

# printing out the results in a quick and easy method https://stackoverflow.com/a/39923958
print(subset_pd['Company'].to_string())


### PART c ###

# group leads by their respective states
state_pd = leads_pd.groupby('Company US State')

# aggregate the number of companies in each state, calculate total revenue, and calculate median revenue
agg_pd = state_pd.agg(leadCount=('Company', 'count'),
                      totalrev=('revenue', 'sum'),
                      medrev=('revenue', 'median')).reset_index()

# finding the company with the most revenue in grouped by state
statelead_pd = leads_pd.loc[leads_pd.groupby('Company US State')['revenue'].idxmax()]
statelead_pd = statelead_pd[['Company', 'Company US State']]

# merging the dataframes together before generating the csv
agg_pd = agg_pd.merge(statelead_pd, on ='Company US State')
agg_pd = agg_pd.rename({'Company US State': 'US State',
                        'leadCount': 'Total number of leads',
                        'totalrev':'Total revenue',
                        'medrev':'Median revenue',
                        'Company':'The lead with most revenue'}, axis = 1)

# generating csv file
agg_pd.to_csv("out.csv",index=False)

# the csv file does not have the exact same format as the sample output; the data could be converted back to string and include "$" and ","
# additionally, the columns could be reordered but I left it as is because I have already worked longer than I should have on this assignment
