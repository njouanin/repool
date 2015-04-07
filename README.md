RethinkDB connection pool
=========================

`repool` is a Python library which provides a connection pool management for accessing a [RethinkDB](http://rethinkdb.com/) database. `repool` creates and maintains a configurable pool of active connection to a RethinkDB database. These connections are then available individually through a basic API.

Internally, `repool` uses the Python [Queue](https://docs.python.org/3.4/library/queue.html) class which is thread-safe. This means that the same connection pool can be share between several threads.


Installation
------------

`repool` is available as a python library on [Pypi](https://pypi.python.org/pypi/repool). Installation is very simple using pip :

    $ pip install repool

This will install `repool` as well as `rethinkdb` dependency.


Basic usage
-----------

A new connection pool using default connection configurations (`host="localhost", port=28015, db="test", auth_key="", timeout=20`) can simply be created by :

    from repool import ConnectionPool

    pool = ConnectionPool()
    cw = pool.acquire()         #returns a ConnectionWrapper instance
    r.table('heroes').run(cw.connection()) #do RethinkDB stuff
    # ...
    pool.release(cw)            #put back connection to the pool
    pool.release_pool()         #release pool (close rethinkdb connections)


Optional arguments
------------------

`ConnectionPool` creation accepts a number of optional arguments :
* `host`, `port`, `db`, `auth_key`, `timeout` : which corresponds to rethinkdb [connect()](http://rethinkdb.com/api/python/#connect) method.
* `pool_size` : set the pool size, ie. the number of connections opened simultaneously (default=10).
* `conn_ttl` : set the connection time to live. Connections older than TTL are automatically closed and re-opened by an internal thread (default=3600 seconds, set to 0 for disable)
* `cleanup`: the interval between each pool cleanup for old connections (default=60 seconds)
