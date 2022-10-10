from persistqueue import FIFOSQLiteQueue

q = FIFOSQLiteQueue(path="./test", multithreading=True)
