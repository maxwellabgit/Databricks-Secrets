import os
import requests
import urllib3

#Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Token is a string which users generate in Databricks separately from this script
TOKEN = 'Databricks API token'
#Scope can be an existing scope or a new scope
SCOPE = 'secrets_maxwellabgit'
#Secrets 'NAME' and 'VALUE' are the key and value pair that we will store in the secrets environment
SECRETS_NAME = 'PASSWORD'
SECRETS_VALUE = 'pass123!'
#We will use this later to specify that we want to replace existing values
OVERWRITE = True

#Get the databricks env
DATABRICKS_INSTANCE_ADDRESS = os.getenv('DATABRICKS_INSTANCE_ADDRESS')
#Build the databricks instance/domain URI string
BASE_URI = 'https://{0}'.format(DATABRICKS_INSTANCE_ADDRESS)

#Build the API URI strings for databricks secrets requests
CREATE_SCPOE = '/api/2.0/secrets/scopes/create'
PUT_SECRET = '/api/2.0/secrets/put'
LIST_SCOPES = '/api/2.0/secrets/scopes/list'
LIST_SECRETS = '/api/2.0/secrets/list'
HEADERS = {'Authorization': 'Bearer {0}'.format(TOKEN)}


#Get a list of existing scopes
response = requests.get(BASE_URI + LIST_SCOPES, headers = HEADERS, verify = False)
if respnse.status_code == 200:
  if bool(response.json()):
    wksp_scopes = [s['name'] for s in response.json()['scopes']]
  else:
    wksp_scopes = []
else:
  print('{0} Failed List {1} secrets: {0}'.format(response.status_code, SCOPE))


#Create the scope if it doesn't exist
if not SCOPE in wksp_scopes:
  create_scope_data = {'scope': SCOPE, 'initial_manage_principal':'users'}
  response = requests.post(BASE_URI + CREATE_SCOPE, headers = HEADERS, json = create_scope_data, verify=False)
  if response.status_code == 200:
    print('Scope was created successfully: {0}'.format(SCOPE))
  else:
    print('Error ({0}) Failed to create scope: {1}'.format(response.status_code, SCOPE))
else:
  print('Scope already exists!')


#get a list of existing secrets within the scope
if SCOPE in wksp_scopes:
  list_secrets_data = {'scope': SCOPE}
  response = requests.get(BASE_URI + LIST_SECRETS, headers = HEADERS, json = list_secrets_data, verify=False)
  if response.status_code == 200:
    if bool(response.json()):
      scope_secrets = [s['key'] for s in response.json()['secrets']]
    else:
      scope_secrets = []
  else:
    print('{0} Failed list {1} secrets: {0}'.format(response.status_code, SCOPE))


#Create secret within scope
if SCOPE in wksp_scopes:
  if not SECRETS_NAME in scope_secrets or OVERWRITE==True:
    if SECRETS_NAME in scope_secrets:
      status = 'updated'
    else:
      status = 'created'

    put_secret = {'scope':SCOPE, 'key':SECRETS_NAME, 'string_value':SECRETS_VALUE}
    response = requests.post(BASE_URI + PUT_SECRET, headers=HEADERS, json=put_secret, verify=False)

    if response.status_code==200:
      print('Secret ({0}) was successfully {1} in scope ({2})'.format(SECRETS_NAME, status, SCOPE))
    else:
      print('Error: ({0}) Failed to create secret: {1}'.format(response.status_code, SECRETS_NAME))
      print(response.text)
  else:
    print('Warning: Secret ({0}) already exists within scope: ({1})!'.format(SECRETS_NAME, SCOPE))
    status = 'not altered'
else:
  print('Warning: Scope does not exist!')


#Ensure the secret value was created successfully
if dbutils.secrets.get(SCOPE, SECRETS_NAME) == SECRETS_VALUE:
  print('Secret was successfully {0}.'.format(status))
  print('Note: Use the following syntax to access databricks secrets ;) ')
  print("\t dbutils.secrets.get('{0}', '{1}')".format(SCOPE, SECRETS_NAME))
