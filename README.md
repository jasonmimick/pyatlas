# pyatlas
Simple lightweight python client for the MongoDB Atlas API.

Getting Started.

```python
from pyatlas import AtlasClient
atlas = AtlasClient(<public_key>,<private_key>)
clusters = atlas.get_clusters()
```

now do stuff...

