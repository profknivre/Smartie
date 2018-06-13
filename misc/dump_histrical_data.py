import shelve
import tempfile
import shutil
from os import unlink
from collections import deque

class NamedTemporaryFile:
    def __enter__(self):
        self.fname = tempfile.mktemp(suffix='.db',prefix='aaaaa__')
        return self.fname

    def __exit__(self, type, value, traceback):
        unlink(self.fname)
        pass

with NamedTemporaryFile() as f:
        shutil.copy('/tmp/historical_data.shelve.db',f)
        ff = f.replace('.db','')
        with shelve.open(ff) as db:
                for k in filter(lambda x: not x.startswith('_'), db.keys()):
                        print(k,list(deque(db.get(k,[]),maxlen=5)))

