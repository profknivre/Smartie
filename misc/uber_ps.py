from pprint import pprint as pp

import psutil

proceses = psutil.process_iter(attrs=['name', 'memory_percent', 'memory_info'])
srtd = sorted(proceses, key=lambda p: p.info['memory_info'].rss)

pp([(p.info['name'], int(p.info['memory_info'].rss / (1024 * 1024))) for p in srtd][-10:])
