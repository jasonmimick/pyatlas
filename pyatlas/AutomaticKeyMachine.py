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
config = {
  'bank_org' : os.environ.get("ATLAS_AKM_ORG_ID") 
 ,'public_key' : os.environ.get("ATLAS_AKM_PUBLIC_KEY") 
 ,'private_key' : os.environ.get("ATLAS_AKM_PRIVATE_KEY") 
 ,'token' : "whiteface55"
}

print( f'pyatlas.AutomaticKeyMachine' )
print(  '+--------------------------' )
print( f'bank_org={bank_org}' )
print( f'public_key={public_key}' )
print( f'private_key={private_key}' )
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

def check_token():
  token = request.args.get('token')
  if token != None and token == TOKEN:
      return True
  else:
      return False
  

#new_org_apikey(self,ip_address):

@app.route('/apiKey')
  if not check_token() throw Exception('invalid token')
  ip_address = request.args.get('ip_address')
  results = atlas_client.new_org_apikey(ip_address,
                                        org_id=bank_org)

  print(f'results={results}')
  fixed = fix_result(results)
  return jsonify(fixed)

@app.route('/newkey/<project_name>')
def new_apikey(project_name):
  if not check_token() throw Exception('invalid token')
  desc = 'automatic-key-machine generated'
  roles = 'ORG_GROUP_CREATOR'
  results = atlas_client.create_apikey(project_name, desc, roles)

  print(f'results={results}')
  fixed = fix_result(results)
  return jsonify(fixed)

@app.route('/whitelist/<project_name>/<public_key>/<ip_address>')
def whitelist(project_name):
  if not check_token() throw Exception('invalid token')
  desc = 'automatic-key-machine generated'
  roles = 'ORG_GROUP_CREATOR'
  results = atlas_client.add_org_apikey_whitelist(
  results = atlas_client.create_apikey(project_name, desc, roles)

  print(f'results={results}')
  fixed = fix_result(results)
  return jsonify(fixed)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
  if not check_token() throw Exception('invalid token')
  return 'You want path: %s' % path

if __name__ == '__main__':
    app.run(host='0.0.0.0')



