import logging
from logging.handlers import (RotatingFileHandler,
                              QueueHandler,
                              QueueListener)
from fansettings import LOG_PATH

f = logging.Formatter('%(asctime)s: %(name)s|%(processName)s|%(process)s|%(levelname)s -- %(message)s')

def getFanLogger(name=None, level=logging.INFO):
    if name is None:
        name = __name__
    log = logging.getLogger(name)
    log.setLevel(level)
    log.propagate = False
    return log

def getFanListener(q, name=None, level=logging.INFO):
    if name is None:
        name = __name__
    log = getFanLogger(name, level)
    fh = RotatingFileHandler(LOG_PATH, maxBytes=8192, backupCount=5)
    fh.setFormatter(f)
    fh.setLevel(level)
    listener = logging.handlers.QueueListener(q, fh)
    log.addHandler(listener)
    return log

def getFanHandler(q, name=None, level=logging.INFO):
    if name is None:
        name = __name__
    log = getFanLogger(name, level)
    qh = logging.handlers.QueueHandler(q)
    qh.setFormatter(f)
    log.addHandler(qh)
    return log
    
