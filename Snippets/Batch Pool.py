import sys
import time
import argparse
import multiprocessing as mp

from tqdm import tqdm
from functools import partial

NUM_PROC = 8

def start_pool(f, vals):
    with mp.Pool(NUM_PROC+1) as p:
        try:
            step  = max(1, min(int(len(vals) / NUM_PROC), 100))
            batch = [vals[i:i+step] for i in range(0, len(vals), step)]
            bound = f.func if isinstance(f, partial) else f
            p.apply_async(bound.__self__.async_task, [])
            print("total: {} batches: {}".format(len(vals), len(batch)))
            for _ in tqdm(p.imap_unordered(f, batch)):
                continue
        except KeyboardInterrupt:
            p.terminate()
            p.join()
        except:
            raise

class Tasker:
    def __init__(self):
        pass
    
    def batch_task(self, items, flag=False):
        if flag:
            for item in items:
                time.sleep(0.01) # work
    
    def async_task(self):
        while True:
            print("Doing the async task.")
            time.sleep(5)

if __name__ == "__main__":
    mp.freeze_support()
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--alpha", dest="alpha", help="perform alpha function",  action="store_true")
    ap.add_argument("-t", "--theta", dest="theta", help="perform theta function",  action="store_true")
    ap.add_argument("--proc",        nargs="?",    help="set number of processes", action="store")
    args = ap.parse_args()
    
    if len(sys.argv) > 1:
        t = Tasker()
        if args.proc:
            NUM_PROC = int(args.proc)
        if args.alpha or args.theta:
            kwargs = {"flag": True}
            items  = range(0, 1000)
            start_pool(partial(t.batch_task, **kwargs), items)
