"""
Module handling classes which handle file locking to avoid deadlocks.
"""

from filelock import FileLock


class FileLockSet:
    """
    Class for grouping file locks.

    A class which groups file locks. By grouping these the locking can
    be handled via a context manager which reduces the risk of the locks
    not being correctly released.

    Parameters
    ----------
    locks : iterable[FileLock], optional
        The locks that should be stored in the FileLockSet.
    """

    def __init__(self, locks=()):
        assert all(isinstance(lock, FileLock) for lock in locks)
        self._locks = list(locks)

    def __enter__(self):
        for lock in self._locks:
            lock.acquire()

    def __exit__(self, _exc_type, _exc_value, _traceback):
        # Release the locks
        for lock in reversed(self._locks):
            lock.release()

    def append(self, new_lock):
        """
        Add a new lock to the FileLockSet.

        Add a new lock to the FileLockSet.

        Parameters
        ----------
        new_lock : FileLock
            The new lock.
        """
        assert isinstance(new_lock, FileLock)
        self._locks.append(new_lock)
