import pytest 
import pprint
import string
import random
import os
from .. pyatlas import AtlasClient
from . testutils import *

@pytest.fixture
def public_key():
  return "PLUJXFDN"
  private_key = "f81c4372-0143-4f72-a4f6-d502b6643c10"

@pytest.fixture
def private_key():
  return "f81c4372-0143-4f72-a4f6-d502b6643c10"

@pytest.fixture
def client(public_key, private_key):
  return AtlasClient(public_key, private_key)

@pytest.fixture
def project_name():
  return new_test_project_name()

@pytest.fixture
def org_id():
  return "599eeea79f78f769464d41a1"

@pytest.fixture
def project(client, project_name, org_id):
  print(f'Creating new project for test project_name:{project_name}') 
  project = client.create_project( project_name, org_id=org_id )
  return project

def test_create_apikey(project):
  project_name=project['content']['name']
  print(f'project_name={project_name}')
  desc = f"test key for project {project_name}"
  key = client.create_apikey(project_name=project_name
                             ,description=desc)
  print(key)
  assert key is not None 


#test_create_programatic_apikey( client() )
