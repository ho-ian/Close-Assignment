from closeio_api import APIError, Client
import pandas as pd

api = Client('api_2D2VjFKpXBMeCq7NonfGCU.5W7EAQ9HtOqPovhLjrXgOh')

# grabbing csv file and reading it into a pandas dataframe
# https://stackoverflow.com/a/50377166 was particularly helpful
url = "https://docs.google.com/spreadsheets/d/1omg1_ZSCMlTLzwv9tON7pkGU10_rDOeJeKmTi_qtf-k/edit#gid=1081785221"
csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=')
csv = pd.read_csv(csv_url)
leads_pd = csv[['Company', 'custom.Company Founded', 'custom.Company Revenue', 'Company US State']]
leads_pd = leads_pd.drop_duplicates()
leads_pd = leads_pd.fillna('')

def lead_parse(x):
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


leads_pd['json'] = leads_pd.apply(lead_parse, axis=1)

def postLead(x):
    try:
        api.post('lead', data=x)
    except APIError as e:
        print("Cannot add lead to org because" + str(e))

leads_pd['json'].apply(postLead)


#grabbing leads
lead_results = api.get('lead', params={
    '_limit': 10,
    '_fields': 'id,display_name,status_label',
    'query': 'status:"Potential" sort:updated'
})

# looking at headers of lead_results; it is a dictionary
#for i in lead_results:
    #print(i)

# grabbing only the data
data = lead_results["data"]


# printing the lead names/company names
#for i in data:
    #print(i["display_name"])