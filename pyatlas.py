import logging
import pprint
import os
import requests
import collections
import json
from datetime import *; 
from dateutil.relativedelta import *
from enum import Enum
import types
from requests.auth import HTTPDigestAuth

import kubernetes

logger = logging.getLogger(__name__)

class ApiVersion(Enum):
  V1 = '/api/atlas/v1.0'
  V2 = '/api/atlas/v2'

class AtlasEnvironment(Enum):
  PRODUCTION = 'https://cloud.mongodb.com'
  STAGING = 'https://cloud-qa.mongodb.com'

class AtlasClient(object):

  def __init__(self,username=os.environ.get("ATLAS_PUBLIC_KEY")
                   ,api_key=os.environ.get("ATLAS_PRIVATE_KEY")
                   ,project_id=os.environ.get("ATLAS_PROJECT")
                   ,base_url="https://cloud.mongodb.com"):
    """ Constructor - pass in username/apikey or public/private key pair for 
        MongoDB Atlas. Override `base_url` for use with an instance of 
        MongoDB Ops Manager.
    """
    self.username = username
    self.api_key = api_key
    self.project_id = project_id
    print(f'...... init project_id={project_id} {self.project_id}')
    self.__project_id = project_id  # cache original if default from OS
    self.digest = HTTPDigestAuth(self.username,self.api_key)

    if isinstance(base_url,AtlasEnvironment):
      self.base_url = base_url.value
    else:
      self.base_url = base_url
    self.api_root = '{}{}'.format(base_url,ApiVersion.V1.value)
    self.default_parmeters = {}
    self.default_parmeters['envelope'] = True
    self.verbose = False
 
  # API
  def organizations(self):
    """ Return a list of organzations available to current api user.
    """
    return self.get('{}/orgs'.format(ApiVersion.V1.value))

  def projects(self):
    """ Alias for groups()
    """
    return self.groups()

  def groups(self):
    """ Return list of groups for this public key.
    """
    return self.get('{}/groups'.format(ApiVersion.V1.value))

  def users(self,org_id):
    """ Return list of users for this organization.
    """
    return self.get('{}/orgs/{}/users'.format(ApiVersion.V1.value,org_id))

  ## Database Users ##
  def database_users(self,project_id=''):
    """ GET /api/atlas/v1.0/groups/{GROUP-ID}/databaseUsers
    """
    project_id = project_id if project_id is not '' else self.__project_id
    return self.get(f'{ApiVersion.V1.value}/groups/{project_id}/databaseUsers')

  def create_programatic_apikey(self
                               ,description='pyatlas api key'
                               ,roles='GROUP_OWNER',project_id=''):
    """ Create a new programatic apikey against the current
        of given group with the given or default (GROUP_OWNER)
        permissions.
    """
    project_id = project_id if project_id is not '' else self.__project_id
    if isinstance(roles, types.StringTypes):
      roles = roles.split(',')
    data = { 'desc' : description, 'roles' : roles }
    return self.post(f'{ApiVersion.V1.value}/groups/{project_id}/apiKeys',body=data)
    
  def create_database_user(self,db_user={},project_id=''):
    """ Create a new db user
    """
    project_id = project_id if project_id is not '' else self.__project_id
    logger.info(f'create_database_user {db_user} {project_id}')
    res = self.post(f'{ApiVersion.V1.value}/groups/{project_id}/databaseUsers',body=db_user)

  def bind(self,cluster_name,ip_address='',bind_details={},project_id=''):
    """ Returns a MongoDB connection string along with 
        a programat
        x1. Need programatic api key to add ip to whitelist
        2. Add ip to whitelist
        3. Generate DB user x with prog api key
        4. get cluster info
        5. assemble connection string and return
    """
    project_id = project_id if project_id is not '' else self.__project_id
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
    project_id = project_id if project_id is not '' else self.__project_id
    return self.get('{}/groups/{}/clusters'.format(ApiVersion.V1.value,project_id))

  def get_cluster(self,cluster_name,project_id=''):
    """ Return cluster by name for this organization.
    """
    print( f'>>>>>>{self.project_id}')
    if project_id == '':
      project_id = self.project_id
    return self.get('{}/groups/{}/clusters/{}'.format(ApiVersion.V1.value,project_id,cluster_name))

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
    response = self.post(f'{ApiVersion.V1.value}/groups/{project_id}/clusters'
                         ,body=provision_details)
    return response

  def delete_cluster(self, cluster_name, project_id ="" ):
    """ Delete the cluster.
    """
    response = self.delete(f'{ApiVersion.V1.value}/groups/{project_id}/clusters/{cluster_name}')
    return response

  ## Fidicuary APIs ##
  def invoices(self,org_id,invoice_id=''):
    """ Return all invoices or a particular invoice.
    """
    return self.get('{}/orgs/{}/invoices/{}'.format(ApiVersion.V1.value,org_id,invoice_id))

  def pending_invoice(self,org_id):
    """ Return the pending invoice for this organization id.
    """
    return self.get('{}/orgs/{}/invoices/pending'.format(ApiVersion.V1.value,org_id))

  def invoice_items(self,org_id,query={}):
    """ Return the line items posted for the
    given _date from the appropriate invoice.
    """
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

  def group_by_name(self,group=''):
    """ Return MongoDB Atlas Project/Group metadata for given project name.
    """
    return self.get('{}/groups/byName/{}'.format(ApiVersion.V1.value,group))

  def envelope(self,parameters={}):
    parameters['envelope'] = True
    return parameters
  
  ### 
  ### raw HTTP methods
  ### 
  def get(self, path, parameters={}):
    parameters = self.envelope(parameters)
    url = '{}{}'.format(self.base_url,path)
    if self.verbose:
      print('AtlasClient get:url={}'.format(url))
    response= requests.get(url,params=parameters,auth=self.digest)
    response.raise_for_status()
    return response.json()

  def post(self, path, parameters={}, body={}):
    headers = { "Content-Type" : "application/json" }
    url = '{}{}'.format(self.base_url,path)
    print(f'url={url} path={path} base_url={self.base_url}')
    response = requests.post(url
                             ,auth=self.digest
                             ,params=self.envelope(parameters)
                             ,data=json.dumps(body)
                             ,headers=headers)
    pprint.pprint(response.json())
    response.raise_for_status()
    return response.json()

  def delete(self, path, parameters={}):
    headers = { "Content-Type" : "application/json" }
    url = '{}{}'.format(self.base_url,path)
    print(f'url={url} path={path} base_url={self.base_url}')
    response = requests.delete(url
                             ,auth=self.digest
                             ,params=self.envelope(parameters)
                             ,headers=headers)
    pprint.pprint(response.json())
    response.raise_for_status()
    return response.json()
