from closeio_api import APIError, Client
from datetime import datetime
import pandas as pd
import re

api = Client('api_2D2VjFKpXBMeCq7NonfGCU.5W7EAQ9HtOqPovhLjrXgOh')

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

def postLead(x):
    try:
        api.post('lead', data=x)
    except APIError as e:
        print("Cannot add lead to org because" + str(e))

# validate and clean phone numbers
# this is a very crude way to validate phone numbers, this misses the edge case with '??' in it because it doesn't check for it
# in the future, if I had time, I would use regex to validate phone numbers more thoroughly
def validateNumber(x):
    phone = x.split('\n')
    number = []
    for i in phone:
        if (not (any(c.isalpha() for c in i)) and len(i)>6): # misses the case with ?? ; would plan on fixing with regex if I had time
            number.append({"phone": i})
    return number

# validate and clean email addresses
# with help from https://stackoverflow.com/a/68755011
def validateEmail(x):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    email = x.split('\n')
    address = []
    for i in email:
        if re.search(regex, i):
            address.append({"email": i})
    return address

# this parses the dataframe into the format we need for posting the contacts as well as cleaning the Contact name fields which are empty
def contactParse(x):
    contact_data = {
        "lead_id": x['id'],
        "name": x['Contact Name'] if x['Contact Name'] else "No Name",
        "phones": x['Contact Phones'],
        "emails": x['Contact Emails']
    }
    return contact_data

def postContact(x):
    try:
        api.post('contact', data=x)
    except APIError as e:
        print(x)
        print("Cannot add contact to org because" + str(e))
        
def getLeads():
    return api.get('lead', params={
        '_fields': 'id,display_name'
    })

def convertDate(x):
    if x:
        return datetime.strptime(x,'%d.%m.%Y').date()
    return x

def convertFloat(x):
    if x:
        rev = x.replace('$','')
        rev = rev.replace(',','')
        return float(rev)
    return x