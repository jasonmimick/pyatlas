import random,string
import pytest 
import pprint
import json
import os
from pyatlas import AtlasClient

@pytest.fixture
def atlas_client():
  public_key = "TVWZPCPO"
  private_key = "67fcfc59-9e11-42a7-aaae-980a144bc119"
  return AtlasClient(public_key, private_key, project_id='5d27b2e89ccf646a9e4d5b82')

@pytest.fixture
def atlas_client_from_env():
  os.environ["ATLAS_PUBLIC_KEY"] = "TVWZPCPO"
  os.environ["ATLAS_PRIVATE_KEY"] = "67fcfc59-9e11-42a7-aaae-980a144bc119"
  os.environ["ATLAS_PROJECT"] ='5d27b2e89ccf646a9e4d5b82'
  return AtlasClient()

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
  response = atlas_client.create_cluster(basic_cluster_details)
  print(response)
  assert response is not None

def xtest_basic_create_cluster(atlas_client_from_env, basic_cluster_details):
  response = atlas_client.create_cluster(basic_cluster_details)
  print(response)
  assert response is not None

def test_basic_get_cluster(atlas_client_from_env, basic_cluster_details):
  cluster_name = basic_cluster_details['name']
  response = atlas_client_from_env.get_cluster(cluster_name)
  print(response)
  pprint.pprint(response)
  assert response is not None

def xtest_basic_delete_cluster(atlas_client, basic_cluster_details):
  cluster_name = basic_cluster_details['name']
  response = atlas_client.delete_cluster(cluster_name)
  print(response)
  assert response is not None
  
