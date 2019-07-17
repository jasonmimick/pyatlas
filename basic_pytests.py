import pytest 
import pprint
from pyatlas import AtlasClient

@pytest.fixture
def atlas_client():
  public_key = "IJVSKWSE"
  private_key = "8586582e-1519-4f8d-a0f3-645c15005c48"
  return AtlasClient(public_key, private_key)

def test_get_groups(atlas_client):
  org_id = '599eec849f78f769464d0dca'
  group = atlas_client.groups(org_id)
  pprint.pprint(group)
  assert group is not None 

def test_get_users(atlas_client):
  org_id = '599eec849f78f769464d0dca'
  users = atlas_client.users(org_id)
  pprint.pprint(users)
  assert users is not None 

def test_get_organizations(atlas_client):
  org_id = '599eec849f78f769464d0dca'
  org = atlas_client.organizations(org_id)
  pprint.pprint(org)
  assert org is not None 
