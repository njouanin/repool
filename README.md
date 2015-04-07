RethinkDB connection pool
=========================

`repool` is a Python library which provides a connection pool management for accessing a [RethinkDB](http://rethinkdb.com/) database. `repool` creates and maintains a configurable pool of active connection to a RethinkDB database. These connections are then available individually through a basic API.


Installation
------------

`repool` is available as a python library on [Pypi](https://pypi.python.org/pypi/repool). Installation is very simple using pip :

    $ pip install repool

This will install `repool` as well as `rethinkdb` dependency.


Basic usage
-----------

A new connection pool using default connection configurations (`host="localhost", port=28015, db="test", auth_key="", timeout=20`) can simply be created by :

    from repool import ConnectionPool

    pool = ConectionPool()
    cw = pool.acquire()         #returns a ConnectionWrapper instance
    conn = cw.connection()      #get the rethinkdb connection instance
    r.table('heroes').run(conn) #do RethinkDB stuff
    # ...
    pool.release(cw)            #put back connection to the pool
    pool.release_pool()         #release pool (close rethinkdb connections)


