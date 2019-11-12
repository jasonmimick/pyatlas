import pytest 
import pprint
from pyatlas import AtlasClient

@pytest.fixture
def atlas_client():
  return AtlasClient()

def test_get_groups(atlas_client):
  group = atlas_client.groups()
  pprint.pprint(group)
  assert group is not None 

def test_get_users(atlas_client):
  org_id = '599eec849f78f769464d0dca'
  users = atlas_client.users(org_id)
  pprint.pprint(users)
  assert users is not None 

def test_get_organizations(atlas_client):
  org = atlas_client.organizations()
  pprint.pprint(org)
  assert org is not None 
