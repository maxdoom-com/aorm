# aorm -- another orm

## Description
This is an super lightweight orm for python.
It supports oursql and sqlite3 as database drivers.

## License
BSD (2-clause)

## Example

```python
from aorm import *
import config

orm.connect_oursql( db=config.db, user=config.user, passwd=config.passwd, host=config.host )

class Users(Model):
    @property
    def inactive(self):
        return not self.active

count = Users.count()
users = Users.all()
user1 = Users.one({'id': 1})
user1.active = True
if user1.inactive:
    user1.active = True
user1.save()
user2 = Users.one({'id': 2})
user2.delete()

class Join(Model):
    pass

data = Join.raw('SELECT u.*, c.* FROM users u, cats c WHERE c.user_id = u.id')
```

## Warning
There might be bugs and issues in here I don't know about (yet).
Use it at your own risk!
