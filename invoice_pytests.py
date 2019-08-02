import pytest 
import pprint
from pyatlas import AtlasClient

TEST_ORGS = ['5ab518f7d383ad7b2a6393fa','599eec849f78f769464d0dca']

@pytest.fixture
def atlas_client():
  public_key = 'jason.mimick@mongodb.com'
  private_key = 'ccb35d26-de5d-4a1b-ba56-a25c5d7655c8'
  return AtlasClient(public_key, private_key)


def test_get_orgs(atlas_client):
  orgs = atlas_client.organizations()
  print(f'{orgs}')
  pprint.pprint(orgs)
  assert orgs is not None 

@pytest.mark.parametrize("org_id", TEST_ORGS) 
def test_get_pending_invoice(atlas_client,org_id):
  invoice = atlas_client.pending_invoice(org_id=org_id)
  pprint.pprint(invoice)
  assert invoice is not None 

@pytest.mark.parametrize("org_id", TEST_ORGS) 
def test_get_items_and_summary(atlas_client,org_id):
  query = { 'endDate' : '2018-08-15T00:00:00Z'}

  items = atlas_client.invoice_items(org_id,query)
  assert items is not None
  pprint.pprint(items)
  total = AtlasClient.summarize_invoice(items)
  pprint.pprint( f'Total all skus: {total}')
  assert total is not None 

