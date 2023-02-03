from closeio_api import APIError, Client
import pandas as pd

api = Client('api_2D2VjFKpXBMeCq7NonfGCU.5W7EAQ9HtOqPovhLjrXgOh')

# grabbing csv file and reading it into a pandas dataframe
# https://stackoverflow.com/a/50377166 was particularly helpful
url = "https://docs.google.com/spreadsheets/d/1omg1_ZSCMlTLzwv9tON7pkGU10_rDOeJeKmTi_qtf-k/edit#gid=1081785221"
csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=')
csv = pd.read_csv(csv_url)

# will want to post all leads first and then add contacts afterwards
leads_pd = csv[['Company', 'custom.Company Founded', 'custom.Company Revenue', 'Company US State']]
leads_pd = leads_pd.drop_duplicates()
leads_pd = leads_pd.fillna('')

# contacts will need to be identified by company, name, email and phone numbers
contacts_pd = csv[['Company', 'Contact Name', 'Contact Emails', 'Contact Phones']]
contacts_pd = contacts_pd.fillna('')

def leadParse(x):
    lead_data = {
        'name': x['Company'],
        'custom.Company Founded': x['custom.Company Founded'] if x['custom.Company Founded'] else None, 
        'custom.Company Revenue': x['custom.Company Revenue'] if x['custom.Company Revenue'] else None,
        'addresses': [
            {
                'state': x['Company US State']
            }
        ]  if x['Company US State'] else None,
    }
    return lead_data


leads_pd['json'] = leads_pd.apply(leadParse, axis=1)

def postLead(x):
    try:
        api.post('lead', data=x)
    except APIError as e:
        print("Cannot add lead to org because" + str(e))

leads_pd['json'].apply(postLead)
