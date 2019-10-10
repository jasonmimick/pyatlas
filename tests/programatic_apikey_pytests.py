import pytest 
import pprint
import string
import random
import os
from pyatlas import AtlasClient

@pytest.fixture
def test_tag(tag_length=5):
 tag_letters = string.ascii_lowercase
 return ''.join(random.choice(tag_letters) for i in range(tag_length))

@pytest.fixture
def client():
  public_key = "PLUJXFDN"
  private_key = "f81c4372-0143-4f72-a4f6-d502b6643c10"
  org_id = "599eeea79f78f769464d41a1"
  return AtlasClient(public_key, private_key, org_id=org_id)

@pytest.fixture
def project(client, test_tag):
  project = client.create_project( f"test-pyatlas-project-{test_tag}")
  pprint.pprint(project)

def test_create_apikey(test_tag,client,project):
  project_name=project['content']['name']
  print(f'project_name={project_name}')
  desc = f"test key for project {project_name}"
  key = client.create_apikey(project_name=project_name
                             ,description=desc)
  pprint.pprint(key)
  assert key is not None 


#test_create_programatic_apikey( client() )
