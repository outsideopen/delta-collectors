from persistqueue import FIFOSQLiteQueue

q = FIFOSQLiteQueue(path=".", multithreading=True)
