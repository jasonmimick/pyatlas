import pytest 
import string
import random
import os
from ..pyatlas import AtlasClient
from .testutils import new_test_project_name

@pytest.fixture
def project_name():
  return new_test_project_name()

@pytest.fixture
def org_id():
  return "599eeea79f78f769464d41a1"
 
@pytest.fixture
def client():
  #public_key = "PLUJXFDN"
  #private_key = "f81c4372-0143-4f72-a4f6-d502b6643c10"
  #client = AtlasClient(public_key, private_key)
  client = AtlasClient()
  return client

def test_create_project(client, project_name, org_id):
  print(f'project_name={project_name}')
  print(f'org_id={org_id}')
  project = client.create_project( project_name, org_id=org_id )
  print(project)
  assert project is not None 

def test_delete_project(client, project_name):
  response = client.delete_project( project_name )
  assert response is not None

