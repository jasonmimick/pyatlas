### simple flask wrapper around pyatlas
### hack away
from flask import Flask
from flask import request
from datetime import datetime, timedelta
from pyatlas import AtlasClient
from flask import jsonify
app = Flask(__name__)


public_key = 'jason.mimick@mongodb.com'
private_key = 'ccb35d26-de5d-4a1b-ba56-a25c5d7655c8'

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

@app.route('/groupCreatorKey/<project_name>')
def new_group_creator_key(project_name):
  desc = 'apikeybank generated'
  roles = 'ORG_GROUP_CREATOR'
  results = AtlasClient.create_apikey(projet_name, desc, roles)

  print(f'results={results}')
  fixed = fix_result(results)
  return jsonify(fixed)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'You want path: %s' % path



