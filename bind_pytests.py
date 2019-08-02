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

def test_basic_bind(atlas_client):
  bind_info = atlas_client.bind('basic-pyatlas-cluster-FOO')
  print(f'bind_info={bind_info}')
  #assert response is not None


