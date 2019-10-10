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

@app.route('/usage_yesterday/<org_id>')
def daily_usage(org_id):
  result = usage_daysback(org_id,days_back=1)
  return fix_result(result)

@app.route('/usage_days_back/<org_id>/<int:days_back>')
def usage_daysback(org_id,days_back=1):
  """ Returns the total daily charge for a given 
      Atlas organization. By default, returns total
      usage cost for yesterday.
  """
  date_N_days_ago = str(datetime.now() - timedelta(days_back))
  date = date_N_days_ago.split(" ")[0]
  date = f'{date}T00:00:00Z'
  query = { 'endDate' : date }
  print(f'query={query}')
  try:
    items = atlas_client.invoice_items(org_id,query)
  except Exception as error:
    print(f'error={error}')
    #if isinstance(error, requests.exceptions.HTTPError):
    #  print('okok')
  
  assert items is not None
  total = AtlasClient.summarize_invoice(items)
  assert total is not None
  results = { 'orgId' : org_id, 
              'daysBack' : days_back,
              'query' : query, 
              'total' : total, 
              'items' : items }
  print(f'results={results}')
  fixed = fix_result(results)
  return jsonify(fixed)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'You want path: %s' % path



