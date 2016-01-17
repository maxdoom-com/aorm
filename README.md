# aorm -- The configuration agnostic ORM

## Description
This is an super lightweight orm for python.
It supports at the moment oursql and sqlite3 as database drivers.

You might take a look at my development plans on <a href="http://maxdoom.com/2016/01/13/aorm-dev-status/" target="_blank">my kanban board</a>.

## Supported Python Versions
This library works with python 2.7.
If you intend to use it with python 3.4 see the definition of the `class Model` and change it like this:

- Python 2.7:
```
class Model(Object):
	__metamodel__ = MetaModel
	...
```
- Python 3.4:
```
class Model(Object, metamodel=MetaModel):
	....
```

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
