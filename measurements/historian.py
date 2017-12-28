import logging
import os
import shelve
from collections import deque
from datetime import datetime
from json import dumps

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

FNAME = '/tmp/historical_data.shelve'
RUNDIRNAME = '/tmp/smartie.runs'


def _engrave(what, where, how_long=1000):
    """

    :param what: object
    :param where: filename
    :param how_long: backlog size
    :return: None
    """
    with shelve.open(where) as db:
        hl = db.get('__how_long',how_long)

        for k, v in filter(lambda x: not x[0].startswith('_'), vars(what).items()):
            hst = db.get(k, deque(maxlen=how_long))
            if hl != how_long:
                hst = deque(hst, maxlen=how_long)
            hst.append(v)
            db[k] = hst
        db['__how_long'] = hl


def engrave(what, how_long=1000):
    """
    save object attributes into FNAME

    :param what: object to be saved
    :param how_long: TTL
    :return: None
    """
    return _engrave(what, FNAME, how_long)


def extract_run(minutes):
    """
    extract  bathroom_humidity from _minutes_ history

    and dump it to separate file

    :param minutes:
    :return: None
    """
    with shelve.open(FNAME) as db:
        bh = db.get('bathroom_humidity')

    assert minutes < len(bh)
    last_run = list(bh)[-minutes:]

    if not os.path.exists(RUNDIRNAME):
        log.info('{} not found, creating'.format(RUNDIRNAME))
        os.mkdir(RUNDIRNAME)

    runname = RUNDIRNAME + '/' + 'run_' + str(datetime.now().strftime('%Y%m%d%H%M')) + '.json'
    with open(runname, 'xt') as f:
        f.write(dumps(last_run))

# def expand_runfiles(how_much=15):
#     p = Path(RUNDIRNAME)
#     p = list(p.glob('run_*.json'))
