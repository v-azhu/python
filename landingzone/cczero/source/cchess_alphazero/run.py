import os
import sys
import multiprocessing as mp
_PATH_ = os.path.dirname(os.path.abspath(__file__))
if _PATH_ not in sys.path:
    sys.path.append(_PATH_)

if __name__ == "__main__":
    # mp.set_start_method('spawn')
    sys.setrecursionlimit(10000)
    import manager
    manager.start()
