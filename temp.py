from closeio_api import APIError, Client
import pandas as pd
import phonenumbers
import re

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

def validateNumber(x):
    phone = x.split('\n')
    number = []
    for i in phone:
        if (not (any(c.isalpha() for c in i)) and len(i)>6): # misses the case with ?? ; would plan on fixing with regex if I had time
            number.append({"phone": i})
    return number

# validate and clean phone numbers
contacts_pd['Contact Phones'] = contacts_pd['Contact Phones'].apply(validateNumber)

def validateEmail(x):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    email = x.split('\n')
    address = []
    for i in email:
        if re.search(regex, i):
            address.append({"email": i})
    return address
# validate and clean email addresses
# with help from https://stackoverflow.com/a/68755011
contacts_pd['Contact Emails'] = contacts_pd['Contact Emails'].apply(validateEmail)

#grabbing leads so we can get lead id's and match them when we post our contacts
lead_results = api.get('lead', params={
    '_fields': 'id,display_name,status_label',
    'query': 'status:"Potential" sort:updated'
})

lead_data = lead_results["data"]
lead_dict = {}

# printing the lead names/company names
for i in lead_data:
    lead_dict[i["display_name"]] = i["id"]
    
def contactParse(x):
    contact_data = {
        "lead_id": lead_dict[x['Company']],
        "name": x['Contact Name'] if x['Contact Name'] else "No Name",
        "phones": x['Contact Phones'],
        "emails": x['Contact Emails']
    }
    return contact_data

contacts_pd['json'] = contacts_pd.apply(contactParse, axis=1)

def postContact(x):
    try:
        api.post('contact', data=x)
    except APIError as e:
        print(x)
        print("Cannot add contact to org because" + str(e))
        
contacts_pd['json'].apply(postContact)