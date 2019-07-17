import random,string
import pytest 
import pprint
import json
from pyatlas import AtlasClient

@pytest.fixture
def atlas_client():
  #public_key = "IJVSKWSE"
  public_key = "TVWZPCPO"
  #private_key = "8586582e-1519-4f8d-a0f3-645c15005c48"
  private_key = "67fcfc59-9e11-42a7-aaae-980a144bc119"
  return AtlasClient(public_key, private_key)

@pytest.fixture
def basic_cluster_details():
  rando = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
  name = f'basic-pyatlas-cluster-FOO'
  print(f'basic_cluster_details.name={name}')
  return {
    'name' : name,
    'cluster_type' : 'REPLICASET',
    'providerSettings' : {
      'providerName' : 'GCP',
      'instanceSizeName' : 'M10',
      'regionName' : 'CENTRAL_US'
    }
  }

def xtest_basic_create_cluster(atlas_client, basic_cluster_details):
  project_id = '5d27b2e89ccf646a9e4d5b82'
  response = atlas_client.create_cluster(project_id,basic_cluster_details)
  print(response)
  assert response is not None

def test_basic_get_cluster(atlas_client, basic_cluster_details):
  project_id = '5d27b2e89ccf646a9e4d5b82'
  cluster_name = basic_cluster_details['name']
  response = atlas_client.clusters(project_id,cluster_name)
  print(response)
  pprint.pprint(response)
  assert response is not None

def xtest_basic_delete_cluster(atlas_client, basic_cluster_details):
  project_id = '5d27b2e89ccf646a9e4d5b82'
  cluster_name = basic_cluster_details['name']
  response = atlas_client.delete_cluster(project_id,cluster_name)
  print(response)
  assert response is not None
  
