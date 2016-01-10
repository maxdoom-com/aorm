#!env/bin/python

from aorm import *
import config

#orm.connect_oursql( db=config.db, user=config.user, passwd=config.passwd, host=config.host )
orm.connect_sqlite3( 'db.sqlite3' )

class Users(Model):
	pass

class Posts(Model):
	pass


p = Posts.create()
p.slug='slug3'
p.title='title 3'
p.content='''Content
of
post
3.
'''
p.save()

p.slug='slug4'
p.save()

posts = Posts.all()
for s in posts:
	print s

first = Posts.one()
print first
first.delete()

for roh in Posts.raw('SELECT id, slug AS test FROM posts'):
	print roh
