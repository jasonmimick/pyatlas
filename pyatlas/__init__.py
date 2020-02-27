import logging
import pprint
import os
import requests
import collections
import json
from datetime import *
from dateutil.relativedelta import *
from enum import Enum
import string
import random
from requests.auth import HTTPDigestAuth
import urllib.request
import kubernetes

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which != logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
logger = logging.getLogger(__name__)

class ApiVersion(Enum):
  A1 = '/api/atlas/v1.0'
  A2 = '/api/atlas/v2'
  CM1 = '/api/public/v1.0' 

class AtlasEnvironment(Enum):
  PRODUCTION = 'https://cloud.mongodb.com'
  STAGING = 'https://cloud-qa.mongodb.com'

class Env(object):
  PUBLIC_KEY = "MCLI_PUBLIC_API_KEY"
  PRIVATE_KEY = "MCLI_PRIVATE_API_KEY"
  ORG_ID = "MCLI_ORG_ID"
  PROJECT_ID = "MCLI_PROJECT_ID"

  @staticmethod
  def get(key):
    return os.getenv(key)

class AtlasClient(object):

  def __init__(self,public_key=Env.get(Env.PUBLIC_KEY)
                   ,private_key=Env.get(Env.PRIVATE_KEY)
                   ,org_id=Env.get(Env.ORG_ID)
                   ,project_id=Env.get(Env.PROJECT_ID)
                   ,base_url="https://cloud.mongodb.com"):
    """ Constructor - pass in username/apikey or public/private key pair for 
        MongoDB Atlas. Override `base_url` for use with an instance of 
        MongoDB Ops Manager.
    """
    self.public_key = public_key 
    self.private_key = private_key
    self.org_id = org_id    
    self.project_id = project_id    

    if isinstance(base_url,AtlasEnvironment):
      self.base_url = base_url.value
    else:
      self.base_url = base_url
    self.api_root = '{}{}'.format(base_url,ApiVersion.A1.value)

  def pyatlas_config(self,verbose=True):
    config = {
      Env.PUBLIC_KEY : self.public_key,
      Env.PRIVATE_KEY : self.private_key,
      Env.ORG_ID : self.org_id,
      Env.PROJECT_ID : self.project_id
    }
    print(f'pyatlas_config={config}')
    return config

  def get_digest(self):
    return HTTPDigestAuth(self.public_key,self.private_key)


  # API
  def organizations(self):
    """ Return a list of organzations available to current api user.
    """
    return self.get('{}/orgs'.format(ApiVersion.A1.value))

  def projects(self):
    """ Alias for groups()
    """
    return self.groups()

  def groups(self):
    """ Return list of groups for this public key.
    """
    #return self.get('{}/groups'.format(ApiVersion.A1.value))
    return self.get('{}/groups'.format(ApiVersion.CM1.value))

  def users(self,org_id=None):
    """ Return list of users for this organization.
    """
    if org_id is None:
      org_id = self.org_id
    return self.get('{}/orgs/{}/users'.format(ApiVersion.A1.value,org_id))

  ## Database Users ##
  def database_users(self,project_id=''):
    """ GET /api/atlas/v1.0/groups/{GROUP-ID}/databaseUsers
    """
    project_id = project_id if project_id != '' else self.__project_id
    return self.get(f'{ApiVersion.A1.value}/groups/{project_id}/databaseUsers')

  def create_project(self
                     ,name
                     ,org_id=None):
    if org_id is None:
      org_id = self.org_id
    project_data = { "name" : name } 
    if org_id:
      project_data["orgId"] = org_id 
    pprint.pprint(project_data)
    project = self.post(f'{ApiVersion.CM1.value}/groups'
                        ,body=project_data)
    pprint.pprint(project)
    print(f'>>>>> {project.keys()}')
    self.project_id = project['content']['id']
    self.org_id = project['content']['orgId']
    return project

  def delete_project(self,name): 
    project = self.project_by_name(project_name=name)
    group_id = project['content']['id']
    logger.info(f'>>>>>>> delete_project name={name} group_id={group_id}')
    response = self.delete(f'{ApiVersion.CM1.value}/groups/{group_id}')
    return response 

  ## TODO - need to expose this in the AutomaticKeyMachine api --
  def new_project_apikey(self,ip_address=None,project_id=None):
    if ip_address is None:
      external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
      print(f'external_ip={external_ip}')
      ip_address=external_ip
    if project_id is None:
      if self.project_id is None:
        raise "No project_id found. Pass or set when creating client"
      project_id=self.project_id

    apikey = self.create_project_apikey(project_id=project_id)
    whitelist = self.add_project_apikey_whitelist(apikey_id=apikey.id
                                              ,ip_address=ip_address
                                              ,project_id=project_id)
    return { 'apikey' : apikey, 'whitelist' : whitelist }

  def create_project_apikey(self
                    ,project_id
                    ,description='pyatlas generated project apikey'
                    ,roles='PROJECT_OWNER'):
    """ Create a new programatic apikey in <project_name>
        with the given or default (GROUP_OWNER)
        permissions.
    """
    print('pyatlas - create_apikey') 
    roles = roles.split(',')
    pprint.pprint(roles)
    data = { 'desc' : description, 'roles' : roles }
    pprint.pprint(data)
    
    target = f'{ApiVersion.CM1.value}/groups/{project_id}/apiKeys'
    print( f'target={target}' )
    print( f'data={data}' )
    response = self.post(target, body=data)
    return response
    
  def add_whitelist_atlas_project(self, ip_address=None):
    if ip_address is None:
      external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
      print(f'external_ip={external_ip}')
      ip_address=external_ip
    data = [ { 'ipAddress' : ip_address, 'comment' : 'pyatlas generated whitelist entry' } ]
    pprint.pprint(data)
    
    target = f'{ApiVersion.A1.value}/groups/{self.project_id}/whitelist'
    print( f'target={target}' )
    print( f'data={data}' )
    response = self.post(target, body=data)
    return response



  def add_project_apikey_whitelist(self
                               ,apikey_id
                               ,ip_address
                               ,project_id):
    """ Add ip address to whitelist for a given
        programatic apikey in <project_name>.
    """
    print('pyatlas - add_whitelist') 
    data = [ { "ipAddress" : f"\"{ip_address}\"" } ]
    pprint.pprint(data)
    
    target = f'{ApiVersion.CM1.value}/groups/{project_id}/apiKeys/{apikey_id}/whitelist'
    print( f'target={target}' )
    print( f'data={data}' )
    response = self.post(target, body=data)
    return response

  def new_org_apikey(self,ip_address):
    apikey = self.create_org_apikey()
    whitelist = self.add_org_apikey_whitelist(apikey.id
                                              ,ip_address)
    return { 'apikey' : apikey, 'whitelist' : whitelist }

  def create_org_apikey(self
                    ,description='pyatlas generated org apikey'
                    ,roles='ORG_GROUP_CREATOR'):
    """ Create a new programatic apikey in <project_name>
        with the given or default (GROUP_OWNER)
        permissions.
    """
    print('pyatlas - create_apikey') 
    roles = roles.split(',')
    pprint.pprint(roles)
    data = { 'desc' : description, 'roles' : roles }
    pprint.pprint(data)
    
    target = f'{ApiVersion.CM1.value}/orgs/{self.org_id}/apiKeys'
    print( f'target={target}' )
    print( f'data={data}' )
    response = self.post(target, body=data)
    return response
    
  def add_org_apikey_whitelist(self
                               ,apikey_id
                               ,ip_address):
    """ Add ip address to whitelist for a given
        programatic apikey in <project_name>.
    """
    print('pyatlas - add_whitelist') 
    data = [ { "ipAddress" : f"\"{ip_address}\"" } ]
    pprint.pprint(data)
    
    target = f'{ApiVersion.CM1.value}/orgs/{self.org_id}/apiKeys/{apikey_id}/whitelist'
    print( f'target={target}' )
    print( f'data={data}' )
    response = self.post(target, body=data)
    return response

  def create_database_user(self,db_user={},project_id=''):
    """ Create a new db user
    """
    project_id = project_id if project_id != '' else self.__project_id
    logger.info(f'create_database_user {db_user} {project_id}')
    res = self.post(f'{ApiVersion.A1.value}/groups/{project_id}/databaseUsers',body=db_user)

  def bind(self,cluster_name,ip_address='',bind_details={},project_id=''):
    """ Returns a MongoDB connection string along with 
        a programat
        x1. Need programatic api key to add ip to whitelist
        2. Add ip to whitelist
        3. Generate DB user x with prog api key
        4. get cluster info
        5. assemble connection string and return
    """
    project_id = project_id if project_id != '' else self.__project_id
    if ip_address == '':
      headers = { 'User-Agent': 'curl/7.61.0'}   # spoof for simple response
      ip = requests.get('http://ifconfig.co', headers)
      ip_address = ip.text.rstrip()
      logger.info(f'bind: looked up ip address: {ip_address}')
    #key = self.create_programatic_apikey(description=description,project_id=project_id)
    db_user = { 'username' : 'foo'
                ,'password' : 'changeme'
                ,'databaseName' : 'admin'
                ,'roles' : [ {'databaseName' : 'admin', 'roleName' : 'dbAdminAnyDatabase'} ] 
    }
    user = self.create_database_user(db_user,project_id=project_id) 
    cluster = self.get_cluster(cluster_name)
    cs = cluster['mongoURIWithOptions'].split('/',1)
    #conn_str = f'{cs[0]//{key['publicKey']}:{key['privateKey']}@{cs[1]}'
    return conn_str

  ## Cluster APIs ##
       
  def clusters(self,project_id=os.environ.get("ATLAS_PROJECT")):
    """ Return list of clusters for this organization.
    """
    project_id = project_id if project_id != '' else self.__project_id
    return self.get('{}/groups/{}/clusters'.format(ApiVersion.A1.value,project_id))

  def get_cluster(self,cluster_name,project_id=''):
    """ Return cluster by name for this organization.
    """
    print( f'>>>>>>{self.project_id}')
    if project_id == '':
      project_id = self.project_id
    return self.get('{}/groups/{}/clusters/{}'.format(ApiVersion.A1.value,project_id,cluster_name))

  def cluster_ready(self,cluster_name,project_id=os.environ.get("ATLAS_PROJECT")):
    """ Return True if and only if cluster stateName is `IDLE`.
    """
    cluster = self.cluster(project_id,cluster_name)
    pprint.pprint(cluster)
    return cluster['stateName'] == 'IDLE'

  def create_cluster(self, provision_details, project_id=""):
    """ Create a cluster.
        The provision_details should be instanace of the
        AtlasCluster CRD
    """
    response = self.post(f'{ApiVersion.A1.value}/groups/{project_id}/clusters'
                         ,body=provision_details)
    return response

  def delete_cluster(self, cluster_name, project_id ="" ):
    """ Delete the cluster.
    """
    response = self.delete(f'{ApiVersion.A1.value}/groups/{project_id}/clusters/{cluster_name}')
    return response

  ## Fidicuary APIs ##
  def invoices(self,org_id=None,invoice_id=''):
    """ Return all invoices or a particular invoice.
    """
    if org_id is None:
      org_id = self.org_id
    return self.get('{}/orgs/{}/invoices/{}'.format(ApiVersion.A1.value,org_id,invoice_id))

  def pending_invoice(self,org_id=None):
    """ Return the pending invoice for this organization id.
    """
    if org_id is None:
      org_id = self.org_id
    return self.get('{}/orgs/{}/invoices/pending'.format(ApiVersion.A1.value,org_id))

  def invoice_items(self,org_id=None,query={}):
    """ Return the line items posted for the
    given _date from the appropriate invoice.
    """
    if org_id is None:
      org_id = self.org_id
    query_end_date = datetime.strptime(query['endDate'],'%Y-%m-%dT%H:%M:%SZ')
    # Given a 'query_end_date' to find the invoice containing the
    # line items for that date we need to find the invoice which 
    # has 'endDate' equal to the end of the month of the `query_end_date`
    query_first_next_month = query_end_date + relativedelta(months=+1) - relativedelta(days=(query_end_date.day-1))
    target_invoices = []
    invoices = self.invoices(org_id)
    if self.verbose:
      print('Searching invoices org_id={}'.format(org_id))
      print('query={} query_end_date={}'.format(query,query_end_date))
      print('Result keys: {}'.format( invoices['content'].keys() ))
      print('Total result count: {}'.format( invoices['content']['totalCount'] ))
    for invoice in invoices['content']['results']:
      #pprint.pprint(invoice)
      end_date = datetime.strptime(invoice['endDate'],'%Y-%m-%dT%H:%M:%SZ')
      if self.verbose: 
        print('invoice({})[\'endDate\']={} end_date={}'.format(invoice['id'],invoice['endDate'],end_date))
      if end_date == query_first_next_month:
        target_invoices.append(invoice)
    
    if self.verbose:  
      print('Target invoices: {}'.format(target_invoices))
 

    target_line_items = []
    for invoice in target_invoices:
      invoice_details = self.invoices(org_id,invoice['id'])       
      print('invoice_details: {}'.format(invoice_details))
      for item in invoice_details['content']['lineItems']:
        end_date = datetime.strptime(item['endDate'],'%Y-%m-%dT%H:%M:%SZ')
        if end_date == query_end_date:
          target_line_items.append(item)
    if self.verbose:
      print('target_line_items: {}'.format(target_line_items)) 
    return target_line_items

  def summarize_invoice(line_items):
    """ Return the sum total for a given list of invoice items.
    """
    sku_summary = AtlasClient.summarize_invoice_items_by_sku(line_items)
    total = 0
    for item in sku_summary:
        total += sku_summary[item]['totalPriceCents']

    return total

  def summarize_invoice_items_by_sku(line_items):
    """ Return a dict summary of line items by SKU.
    """
    sku_summary = {}
    for item in line_items:
      if item['sku'] not in sku_summary:
        sku_summary[item['sku']]= { 'totalPriceCents' : 0 }
      c = sku_summary[ item['sku'] ]['totalPriceCents'] + item['totalPriceCents']
      si = { 'totalPriceCents'  : c,
             'sku' : item['sku'],
             'endDate' : item['endDate'] }
      sku_summary[ item['sku'] ] = si

    return sku_summary


  def project_by_name(self,project_name=''):
    """ Return MongoDB Atlas Project/Group metadata for given project name.
    """
    logger.debug(f'project_by_name project_name={project_name}')
    return self.get('{}/groups/byName/{}'.format(ApiVersion.CM1.value,project_name))

  def envelope(self,parameters={}):
    parameters['envelope'] = True
    return parameters
  
  ### 
  ### raw HTTP methods
  ### 
  def get(self, path, parameters={}):
    parameters = self.envelope(parameters)
    url = '{}{}'.format(self.base_url,path)
    logger.info('AtlasClient get:url={}'.format(url))
    response= requests.get(url,params=parameters,auth=self.get_digest())
    logger.info(f' response.json()={response.json()}')
    response.raise_for_status()
    return response.json()

  def post(self, path, parameters={}, body={}):
    headers = { "Content-Type" : "application/json" }
    url = '{}{}'.format(self.base_url,path)
    self.pyatlas_config()
    print(f'url={url} path={path} base_url={self.base_url}')
    pprint.pprint(body)
    response = requests.post(url
                             ,auth=self.get_digest()
                             ,params=self.envelope(parameters)
                             ,data=json.dumps(body)
                             ,headers=headers)
    pprint.pprint(response.json())
    response.raise_for_status()
    return response.json()

  def delete(self, path, parameters={}):
    headers = { "Content-Type" : "application/json" }
    url = '{}{}'.format(self.base_url,path)
    self.pyatlas_config()
    print(f'url={url} path={path} base_url={self.base_url}')
    response = requests.delete(url
                             ,auth=self.get_digest()
                             ,params=self.envelope(parameters)
                             ,headers=headers)
    pprint.pprint(response.json())
    response.raise_for_status()
    return response.json()
