import logging
import logging.config
from fansettings import LOG_PATH, LOG_FORMAT
from multiprocessing import Queue as Q

q = Q()

LOGGING = {
    'version':1,
    'handlers':{
        'fileHandler':{
            'class':'logging.handlers.RotatingFileHandler',
            'formatter':'full',
            'filename':LOG_PATH,
            'maxBytes':1024*1024, # 1 MB
            'backupCount':5
            },
        'streamHandler':{
            'class':'logging.StreamHandler',
            'formatter':'brief',
            'level':'DEBUG'
            },
        'qhandler':{
            'class':'logging.handlers.QueueHandler',
            'queue':q,
            'level':'DEBUG'
        }
    },
    'loggers':{
        'qlogger':{
            'handlers':['fileHandler','streamHandler','qhandler'],
            'level':'DEBUG'
            }
        },
    'formatters':{
        'full':{
            'format':'%(asctime)s: %(module)20s.%(funcName)-20s#%(lineno)-5d|%(processName)-20s|%(process)d|%(levelname)s -- %(message)s',
            },
        'brief':{
            'format':'%(asctime)s [%(name)s - %(levelname)s]: %(message)s'
            }
        }
    }

                        
def getFanLog(config):
    logging.config.dictConfig(config)
    log = logging.getLogger('qlogger')
    fh = {x.get_name():x for x in log.handlers}['fileHandler']
    q = {x.get_name():x for x in log.handlers}['qhandler'].queue
    sh = {x.get_name():x for x in log.handlers}['streamHandler']
    ql = logging.handlers.QueueListener(q, fh, sh)
    log.handlers = [x for x in log.handlers if x.name != 'fileHandler']
    return log, ql, ql.queue

