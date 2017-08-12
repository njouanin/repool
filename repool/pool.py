# Copyright (C) 2014  Nicolas Jouanin
#
# This file is part of repool.
#
# Repool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Repool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Repool.  If not, see <http://www.gnu.org/licenses/>.

import rethinkdb as r
import sys
import time
import logging
from threading import Lock, Thread, Event

is_py2 = sys.version[0] == '2'
if is_py2:
    from Queue import Queue
else:
    from queue import Queue


logger = logging.getLogger(__name__)


class PoolException(Exception):
    pass


class ConnectionWrapper(object):
    def __init__(self, pool, conn=None, **kwargs):
        self._pool = pool
        if conn is None:
            self._conn = r.connect(**kwargs)
        else:
            self._conn = conn
        self.connected_at = time.time()

    @property
    def connection(self):
        return self._conn


class ConnectionPool(object):
    """A rethinkDB connection pool
    >>> pool = ConnectionPool()
    >>> with pool.acquire() as conn:
            conn.do_something()
    """

    def __init__(self, **kwargs):
        """Create a new connection pool with the specified arguments.
        :param min_size: Minimum connection pool size
        :param max_size: Maximum connection pool size
        :param conn_ttl: Connection time-to-live (in seconds).
        """
        self.pool_size = int(kwargs.get('pool_size', 10))
        self.conn_ttl = int(kwargs.get('conn_ttl', 3600))
        self.cleanup_timeout = int(kwargs.get('cleanup', 60))
        self._conn_args = kwargs
        self._conn_args.pop('pool_size', None)
        self._conn_args.pop('conn_ttl', None)
        self._conn_args.pop('cleanup', None)

        self._pool = Queue()
        self._pool_lock = Lock()
        self._pool_lock.acquire()
        for i in range(0, self.pool_size):
            self._pool.put(self.new_conn())
        self._current_acquired = 0
        self._pool_lock.release()

        if self.cleanup_timeout > 0:
            self._thread_event = Event()
            self._cleanup_thread = Thread(target=self._cleanup, name='Cleanup thread',
                                          args=(self._thread_event, self.cleanup_timeout))
            self._cleanup_thread.daemon = True
            self._cleanup_thread.start()
        else:
            self._cleanup_thread = None

    def new_conn(self):
        """
        Create a new ConnectionWrapper instance
        :return:
        """
        """
        :return:
        """
        logger.debug("Opening new connection to rethinkdb with args=%s" % self._conn_args)
        return ConnectionWrapper(self._pool, **self._conn_args)

    def acquire(self, timeout=None):
        """Acquire a connection
        :param timeout: If provided, seconds to wait for a connection before raising
            Queue.Empty. If not provided, blocks indefinitely.
        :returns: Returns a RethinkDB connection
        :raises Empty: No resources are available before timeout.
        """
        self._pool_lock.acquire()
        if timeout is None:
            conn_wrapper = self._pool.get_nowait()
        else:
            conn_wrapper = self._pool.get(True, timeout)
        self._current_acquired += 1
        self._pool_lock.release()
        return conn_wrapper.connection

    def release(self, conn):
        """Release a previously acquired connection.
        The connection is put back into the pool."""
        self._pool_lock.acquire()
        self._pool.put(ConnectionWrapper(self._pool, conn))
        self._current_acquired -= 1
        self._pool_lock.release()

    def empty(self):
        """Check pool emptyness
        """
        return self._pool.empty()

    def release_pool(self):
        """Release pool and all its connection"""
        if self._current_acquired > 0:
            raise PoolException("Can't release pool: %d connection(s) still acquired" % self._current_acquired)
        while not self._pool.empty():
            conn = self.acquire()
            conn.close()
        if self._cleanup_thread is not None:
            self._thread_event.set()
            self._cleanup_thread.join()
        self._pool = None

    def _cleanup(self, stop_event, timeout):
        logger.debug("Starting cleanup thread")
        while not stop_event.is_set():
            import time
            stop_event.wait(timeout)
            logger.debug("Cleanup thread running...")
            now = time.time()
            queue_tmp = Queue()
            try:
                self._pool_lock.acquire()
                nb = 0
                while not self._pool.empty():
                    conn_wrapper = self._pool.get_nowait()
                    if (now - conn_wrapper.connected_at) > self.conn_ttl:
                        conn_wrapper.connection.close()
                        del conn_wrapper
                        queue_tmp.put(self.new_conn())
                        nb += 1
                    else:
                        queue_tmp.put(conn_wrapper)
                self._pool = queue_tmp
                self._pool_lock.release()
                logger.debug(" %d connection(s) cleaned" % nb)
            except Exception as e:
                logger.exception(e)
                pass
        logger.debug("Cleanup thread ending")
