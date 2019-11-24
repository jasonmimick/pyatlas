import pytest 
import pprint
import string
import random
import os
from pyatlas import AtlasClient
#from testutils import *

@pytest.fixture
def public_key():
  return "NGKMIHEO"

@pytest.fixture
def private_key():
  return "66bcc7de-b0de-4d8d-9695-ef97637c6895"

@pytest.fixture
def client(public_key, private_key):
  return AtlasClient(public_key, private_key)

@pytest.fixture
def project_name():
  return new_test_project_name()

@pytest.fixture
def org_id():
  return "5d371dda553855dd17d4fcf9"

@pytest.fixture
def project(client, project_name, org_id):
  print(f'Creating new project for test project_name:{project_name}') 
  project = client.create_project( project_name, org_id=org_id )
  return project

def test_create_apikey(client,project):
  project_name=project['content']['name']
  print(f'project_name={project_name}')
  desc = f"test key for project {project_name}"
  key = client.create_apikey(project_name=project_name
                             ,description=desc)
  print('-------------------- start generated apikey --------------------')
  print(key)
  print('-------------------- end generated apikey --------------------')
  assert key is not None 

## utils

def random_token(N=5):
  token=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
  print(f'token={token}')
  return token

def new_test_project_name():
  project_name=f'pyatlas-test-{random_token()}'
  return project_name
