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
#!/usr/bin/env python2.7

from aorm import *

orm.connect_sqlite3( 'test.db' )

#
# Models
#
class Users(Model):
    @property
    def posts(self):
    	return Posts.all({
    		'author':self.id,
    	})

class Posts(Model):
    pass

class Raw(Model):
	pass

#
# Helpers
#



# HELPERS
def mkuser(email, password):
	u=Users.create()
	u.email=email
	u.password=password
	u.save()
	return u

def mkpost(slug, title, content, user):
	p=Posts.create()
	p.slug=slug
	p.title=title
	p.content=content
	p.author=user.id
	p.save()
	return p


#
# Real test
#
u1 = mkuser('i@some.where', 'my password')
u2 = mkuser('i@some.where.else', 'my other password')

p1 = mkpost('post1', 'post1', '''this is a post''', u1)
p2 = mkpost('post2', 'post2', '''this is another post''', u2)
p3 = mkpost('post3', 'post3', '''this is the third post''', u1)

#
# Test #1
#
print("# Expected result: post1 post3")
test1 = Users.one({ 'email':'i@some.where' })
for post in test1.posts:
	print( post.slug )

#
# Test #2
#
print("# Expected result: none")
test2 = Users.one({ 'id':2 })
for post in test2.posts:
	post.delete()

for post in Posts.all({ 'author':2 }):
	print(post.slug)

#
# Test #3
#
print("# Expected results: 2 2")
print("Users.count after tests: %d" % Users.count())
print("Posts.count after tests: %d" % Posts.count())
```

## Warning
There might be bugs and issues in here I don't know about (yet).
Use it at your own risk!
