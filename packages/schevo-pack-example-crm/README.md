# schevo-pack-example-crm

Example CRM schema pack for Schevo.

## Usage

```python
from schevo_core import MigrationRegistry, upcast_to_latest
from schevo_pack_example_crm import SCHEMA_ID, register

registry = MigrationRegistry()
register(registry)

record = {"schema_version": 1, "customerId": "c-1", "name": "Ada", "age": "42"}
latest = upcast_to_latest(record, SCHEMA_ID, registry)
```
