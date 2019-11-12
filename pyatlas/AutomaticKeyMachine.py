### simple flask wrapper around pyatlas
### hack away
from flask import Flask
import os
from flask import request
from datetime import datetime, timedelta
from pyatlas import AtlasClient
from flask import jsonify
app = Flask(__name__)


## This is the orgId for the parent org for all
#the apikeys created by this automatic-key-machine
#
bank_org = os.environ.get("ATLAS_AKM_ORGID") 
public_key = os.environ.get("ATLAS_AKM_PUBLICKEY") 
private_key = os.environ.get("ATLAS_AKM_PRIVATEKEY") 

bank_org = '5dc97dd1cf09a2535465a5f8'
public_key = 'AMQGBLIO'
private_key = '833a31fd-0eaa-4ff1-9a61-633d46a278c8'

atlas_client = AtlasClient(public_key, private_key)
atlas_client.verbose = True


def fix_result(result):
  keys = request.args.get('keys') 
  if keys is not None:
    fixed_result = {}
    for key in keys.split(','):
      fixed_result[key]=result.get(key)
      return fixed_result
  else:
    return result

@app.route('/newproject/<project_name>')
def new_project(project_name):
  desc = 'apikeybank generated'
  roles = 'ORG_GROUP_CREATOR'
  results = atlas_client.create_project(project_name,
                                        org_id=bank_org)

  print(f'results={results}')
  fixed = fix_result(results)
  return jsonify(fixed)

@app.route('/newkey/<project_name>')
def new_apikey(project_name):
  desc = 'apikeybank generated'
  roles = 'ORG_GROUP_CREATOR'
  results = atlas_client.create_apikey(project_name, desc, roles)

  print(f'results={results}')
  fixed = fix_result(results)
  return jsonify(fixed)

@app.route('/newwhitelist/<project_name>')
def new_whitelist(project_name):
  desc = 'apikeybank generated'
  roles = 'ORG_GROUP_CREATOR'
  results = atlas_client.create_apikey(project_name, desc, roles)

  print(f'results={results}')
  fixed = fix_result(results)
  return jsonify(fixed)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'You want path: %s' % path



