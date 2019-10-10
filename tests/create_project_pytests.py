import pytest 
import pprint
import string
import random
import os
from pyatlas import AtlasClient

@pytest.fixture
def client():
  public_key = "PLUJXFDN"
  private_key = "f81c4372-0143-4f72-a4f6-d502b6643c10"
  org_id = "599eeea79f78f769464d41a1"
  client = AtlasClient(public_key, private_key)
  client.org_id=org_id
  return client

def test_create_project(client):
  project = client.create_project( f"test-pyatlas-project-{client.unique_tag}")
  pprint.pprint(project)
  assert project is not None 

