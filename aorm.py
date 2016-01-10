"""
An ORM (AORM) for Python using OurSql.
============================================
COPYRIGHT (C) 2015 Nico Hoffmann
--------------------------------------------
Limitations:

Aorm only uses oursql or sqlite3. It should
be quite simple to port it to other database
drivers as long as these use parameterized
queries.

--------------------------------------------
How it works:
--------------------------------------------
from aorm import orm, Model
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

"""

__author__ = 'Nico Hoffmann <n@maxdoom.com>'
__credits__ = '''The Roots:

There is a whole bunch of ORMs that influenced this tiny orm.

- Most noteable is idiorm/paris from the php world.
- SQLObject is been an inspiration as well.
'''

import re as _re
from collections import OrderedDict



_camel_case_pattern = _re.compile(r'([A-Z])')



def underscorify(name):
    out = _camel_case_pattern.sub(lambda x: '_' + x.group(1).lower(), name)
    if out[0]=='_':
        out = out[1:]
    return out



class orm:
    __connection = None
    driver = None
    
    @staticmethod
    def connect_oursql(db, user, passwd, host='localhost', **args):
        import oursql
        orm.driver = 'oursql'
        orm.__connection = oursql.Connection(host, user, passwd, db=db, default_cursor=oursql.DictCursor, **args)
    
    @staticmethod
    def connect_sqlite3(file, isolation_level=None, **args):
        # isolation_level=None means autocommit
        import sqlite3
        orm.driver = 'sqlite3'
        orm.__connection = sqlite3.connect(file, isolation_level=isolation_level, **args)
        orm.__connection.row_factory = sqlite3.Row
    
    @staticmethod
    def cursor():
        return orm.__connection.cursor()



class MetaModel(type):
    def __new__(cls, name, bases, args):
        if name in globals():
            return globals()[name]
        else:
            Type = type.__new__(cls, name, bases, args)
            
            if not '__table__' in Type.__dict__:
                Type.__table__ = underscorify(name)
            
            if not '__id__' in Type.__dict__:
                Type.__id__ = 'id' # this is the one auto increment column
            
            return Type



class Object(object):
    pass



class Model(Object):
    """
        The base class of all models.
    """
    __metaclass__ = MetaModel
    
    def __setattr__(self, key, value):
        """
            Used to set attributes. Note that this orm doesn't allow to store fields that
            start with an underscore. Fields with an underscore at the beginning have
            special meanings.
        """
        if not key.startswith('_'):
            self._bad = True
        super(Object, self).__setattr__(key, value)

    def __repr__(self):
        """
            Returns a representation of the data of this record.
        """
        return '; '.join( [ '%s=%s' % ( k, self.__dict__[k] ) for k in self.__dict__ ] )

    @property
    def _data(self):
        """
            Returns a dict of key:value pairs of this records data.
        """
        return { k: self.__dict__[k]   for k in self.__dict__ if not k.startswith('_') }

    @property
    def _fields(self):
        """
            Returns the fields of this record.
        """
        return [ k for k in self.__dict__ if not k.startswith('_') and k != self._id ]

    @classmethod
    def create(cls, data={}, mode='insert', bad=True):
        """
            Used to create a new item of the subclass of Model.
            So you may:
                class MyModel(Model):
                    pass
                
                m = MyModel.create()
                m.something = 123
                m.save()
        """
        return cls(data, mode, bad)

    def __init__(self, data={}, mode='insert', bad=True):
        """
            Create an instance of this model.
            
            mode: 'insert'|
                if 'insert', the record may be inserted with save(), otherwise it's going to be an update
            bad: True|False
                if False, the record will be treated as unchanged
        """
        
        
        ### DRIVER SPECIFIC ###
        
        if orm.driver == 'sqlite3':
            for k in data.keys():
                setattr(self, k, data[k])
        else:
            for k in data:
                setattr(self, k, data[k])
        
        
        ### UNIFORM ###
        
        self._table = self.__table__
        self._id = self.__id__
        self._mode = mode
        self._bad = bad
    
    def save(self):
        """
            Save this record. Maybe an insert or save, depending on the way it was created.
            See __init__(...).
        """
        if self._bad:
            if self._mode == 'insert':
                fields = self._fields
                query = '''INSERT INTO `%s`( %s ) VALUES( %s )''' % (self._table, ','.join(fields) , ','.join('?'*len(fields)))
                
                cursor = orm.cursor()
                cursor.execute(query, [ getattr(self, k) for k in fields ])
                
                self.__setattr__(self._id, cursor.lastrowid)
                self._bad = False
                self._mode = 'update'
            else: # update
                fields = self._fields
                query = '''UPDATE `%s` SET %s WHERE `%s`=?''' % (self._table, ','.join('`%s`=?' % k for k in fields), self._id)
                
                cursor = orm.cursor()
                cursor.execute(query, [ getattr(self, k) for k in fields ] + [ getattr(self, self._id) ])
                
                self._bad = False
                self._mode = 'update'
    
    
    @classmethod
    def __prepare(cls, conditions={}, limit=None, offset=None, order_by=None, group_by=None, fields='*'):
        """
            Builds SQL queries.
            
            Beware that the arguments limit, offset, order_by, group_by and fields might be subject
            to code injections. Don't use unsanitized user supplied input for these fields!
            
            The keys for the conditions might be entry points to code injections as well. Beware!
        """
        where = 'WHERE' if len(conditions) else 'WHERE 1=1'
        
        p = OrderedDict(**conditions)
        
        query = ' AND '.join( ['(`%s`=?)'%k for k in p.keys()] )
        
        limit   = '' if not limit   else 'LIMIT %d' % int(limit)
        offset   = '' if not offset   else 'OFFSET %d'   % int(offset)
        group_by = '' if not group_by else 'GROUP BY %s' % group_by
        order_by = '' if not order_by else 'ORDER BY %s' % order_by
        
        sql = '''SELECT {fields} FROM {table} {where} {query} {group_by} {order_by} {limit} {offset}'''.format(
            table=cls.__table__,
            where=where,
            query=query,
            limit=limit,
            offset=offset,
            group_by=group_by,
            order_by=order_by,
            fields=fields
        )
        
        return sql, p.values()
    
    @classmethod
    def one(cls, conditions={}, offset=None, order_by=None, group_by=None, fields='*'):
        """
            Returns the first matching element or None.
        """
        for item in cls.all(conditions=conditions, limit=1, offset=offset, order_by=order_by, group_by=group_by, fields=fields):
            return item
    
    @classmethod
    def all(cls, conditions={}, limit=None, offset=None, order_by=None, group_by=None, fields='*'):
        """
            Returns all matching elements.
        """
        sql, values = cls.__prepare(conditions=conditions, limit=limit, offset=offset, order_by=order_by, group_by=group_by, fields=fields)
        
        cursor = orm.cursor()
        cursor.execute(sql, values)
        
        for row in cursor:
            yield cls(data=row, mode='update', bad=False)
    
    @classmethod
    def raw(cls, query, params=()):
        """
            Returns all matching elements.
            
            As this orm doesn't inspect your database you might for instance define a Model for a SQL join and select this.
            
            For instance:
                class SomeFeatures(Model):
                    pass
                
                f = SomeFeatures.raw('SELECT * FROM some, feature WHERE feature.some_id = some.id')
        """
        cursor = orm.cursor()
        cursor.execute(query, params)
        
        for row in cursor:
            yield cls(data=row, mode='update', bad=False)
    
    @classmethod
    def count(cls, conditions={}, group_by=None):
        """
            Returns the count of entries matching the query.
        """
        sql, values = cls.__prepare(conditions=conditions, fields='COUNT(*) AS count', group_by=group_by)
        cursor = orm.cursor()
        cursor.execute(sql, values)
        
        for row in cursor:
            return row['count']
        
        return 0 # as fallback
    
    
    def delete(self):
        """
            Delete a loaded instance.
        """
        query = '''DELETE FROM `{table}` WHERE `{id}`=?'''.format( table = self._table, id=self._id)
        
        cursor = orm.cursor()
        cursor.execute(query, [ getattr(self, self._id) ])

__all__ = [
    'orm', 'Model',
]
