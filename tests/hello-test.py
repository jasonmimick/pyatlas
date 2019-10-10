import pprint
from pyatlas import AtlasClient

public_key = "IJVSKWSE"
private_key = "8586582e-1519-4f8d-a0f3-645c15005c48"
atlas_client = AtlasClient(public_key, private_key,project_id='5d36251779358e2b6002872d')
group = atlas_client.groups()
pprint.pprint(group)

