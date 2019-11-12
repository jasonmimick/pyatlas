# pyatlas
Simple lightweight python client for the MongoDB Atlas API.

Getting Started.

```bash
$export MONGODB_ATLAS_PUBLIC_KEY="xxx"
$export MONGODB_ATLAS_PRIVATE_KEY="xxx"
```
then,
```python
from pyatlas import AtlasClient
atlas = AtlasClient()
clusters = atlas.clusters()
```

now do stuff...

or you can
```bash
$export MONGODB_ATLAS_USERNAME="xxx"
$export MONGODB_ATLAS_PERSONAL_APIKEY="xxx"
```

