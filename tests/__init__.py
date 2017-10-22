import logging

logging.basicConfig(level=logging.DEBUG)

logging.getLogger().setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logging.getLogger().addHandler(ch)
