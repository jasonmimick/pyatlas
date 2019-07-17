# pyatlas
Simple lightweight python client for the MongoDB Atlas API.

Getting Started.

```bash
$export ATLAS_PUBLIC_KEY="xxx"
$export ATLAS_PRIVATE_KEY="xxx"
$export ATLAS_PROJECT="xxx"
```
then,
```python
from pyatlas import AtlasClient
atlas = AtlasClient()
clusters = atlas.clusters()
```

now do stuff...

