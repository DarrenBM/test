# @TO-DO:
#    - Add sentiment check sampling (with variable to control rate)
#    - Use multiprocessing.Event to control starting, stopping, waiting
#    - Modify archiving procedure so that stream is unbroken--keep streaming into
#      old queue, start new streamer, stop old streamer, start DB workers,
#      then merge old queue into new queue.

###########
# Imports #
###########

#from random import randint

import multiprocessing

# streaming
from twython import TwythonStreamer, Twython

# Text/linguistic processing
from textblob import TextBlob

# Fan settings
from fansettings_new import *
from db_spec import *
from credentials_new import CREDENTIALS


# Dates
## for simple parsing of Twitter timestamps
from dateutil import parser as date_parser

## other date processing
from datetime import datetime as dt
import time

#json parsing
from json import dumps as json_dumps

# logging and errors
import logging
import traceback
from queue import Empty
from twython import TwythonError
from logging.handlers import QueueHandler
from sqlalchemy.exc import IntegrityError, OperationalError
from http.client import IncompleteRead
from requests.exceptions import ChunkedEncodingError

###########
# Globals #
###########

# Set duration for sleeping processes when queues are empty
# might be able to omit this setting by using Queue.get(block=True)
SLEEP_TIME = .1


class StreamWorker(multiprocessing.Process):
    """
    Subclass implementation of multiprocessing that allows a
    FanTwython object to run in its own process.
    """
    def __init__(self, q, msgq, errq, countq, db_path=DB_PATH, credentials=CREDENTIALS, chunk_size=10, **params):
        multiprocessing.Process.__init__(self)
        self.q = q
        self.msgq = msgq
        self.errq = errq
        self.countq = countq
        self.db_path = db_path
        self.credentials = credentials
        self.chunk_size = chunk_size
        self.params = params
        self.log = None
        self.streamer = None
        self.streamsession_id = None
        
    def run(self):
        qh = QueueHandler(self.errq)
        qh.setLevel(logging.INFO)
        
        self.log = logging.getLogger('SW-{}'.format(self.pid))
        self.log.setLevel(logging.INFO)
        self.log.propagate = False
        self.log.addHandler(qh)
        self.log.info('{0} ({1}) now running'.format(self.name, self.pid)) # @DEBUG
        self.stream()


    def stream(self):
        self.log.info('StreamWorker {} starting stream with:\n    {}'.format(
            self.pid,
            json_dumps({str(k): str(v) for k, v in self.params.items()})))

        # Get new StreamSession from DB
        session = get_session(self.db_path)
        ss = session.merge(StreamSession(starttime=dt.now()))
        session.commit()
        self.streamsession_id = ss.id
        session.close()

        # create streamer
        self.streamer = FanTwython(self.q, self.msgq, self.log, self.countq, self.streamsession_id, self.credentials, chunk_size=self.chunk_size)

        # stream tweets
        try:
            self.streamer.statuses.filter(**self.params)

        except (IncompleteRead, ChunkedEncodingError) as e:
            self.log.exception(e)
            self.restart_stream()

        except Exception as e:
            tb = traceback.format_exc()
            print('ERROR STREAMING') #@DEBUG
            print(tb)
            print(e)
            self.log.exception(e)
            self.restart_stream()
            
        except ValueError:
            raise

    def stop_stream(self):
        self.log.info('Stopping stream.')
        self.streamer.disconnect()
        t = dt.now()
        session = get_session(self.db_path)
        ss = session.merge(StreamSession(id=self.streamsession_id))
        ss.endtime = t
        session.commit()
        session.close()

    def restart_stream(self):
        self.stop_stream()
        self.stream()
        

class FanTwython(TwythonStreamer):
    """
    Adds a queue to a TwythonStreamer object so that results from the
    stream can be passed to other processes.
    """
    def __init__(self, q, msgq, log, countq, ssid, credentials, chunk_size=10):
        TwythonStreamer.__init__(self,
                                 credentials['APP_KEY'],
                                 credentials['APP_SECRET'],
                                 credentials['ACCESS_KEY'],
                                 credentials['ACCESS_SECRET'],
                                 handlers=['delete',
                                           'scrub_geo',
                                           'limit',
                                           'status_withheld',
                                           'disconnect',
                                           'warning'],
                                 chunk_size=chunk_size)
        self.queue = q
        self.msgq = msgq
        self.log = log
        self.countq = countq
        self.streamsession_id = ssid

    def on_success(self, data):
        data['streamsession_id'] = self.streamsession_id
        try:
            self.queue.put((TWEET_MESSAGE, data))
        except Exception as e:
            self.log.exception('Error enqueing tweet data from stream')
        else:
            self.countq.put(1)
        finally:
            try: # Check for stop message
                msg = self.msgq.get_nowait()
            except Empty:
                pass
            else:
                if msg == STOP_MESSAGE:
                    self.disconnect() # stop the stream
                    self.queue.put((STOP_STREAM_MESSAGE, dt.now())) 
                    self.queue.put((STOP_MESSAGE, None))


    def on_error(self, status_code, data):
        # @TO-DO: handle Twython errors - see https://twython.readthedocs.org/en/latest/api.html#twython.TwythonStreamer.disconnect
        print('\n\n' + ('*'*70))
        print('Twython error')
        print('*'*70)
        print ( status_code, data )
        msg = '{0}\nTwython Error:\n{1}\n{0}\n\n'.format(
            '*'*70, json_dumps(data))
        e = TwythonError(msg, status_code)
        self.log.error('twythonError', '{}:{}'.format(
            status_code,
            json_dumps(data)))
        raise(e)
        
        


    ##################################################################
    # Other message handlers
    ##################################################################

    def on_delete(self, data):
        self.log.warning('Delete message received from stream: ' + data)
        pass

    def on_scrub_geo(self, data):
        self.log.warning('scrub_geo message received from stream: ' + data)
        pass

    def on_limit(self, data):
        self.log.warning('limit message received from stream: ' + data)
        pass

    def on_status_withheld(self, data):
        self.log.warningu('status_withheld message received from stream' + data)
        pass

    def on_user_withheld(self, data):
        self.log.warning('user_withheld message received from stream' + data)
        pass

    def on_disconnect(self, data):
        self.log.warning('disconnect message received from stream' + data)
        pass

    def on_warning(self, data):
        self.log.warning('warning message received from stream' + data)
        pass

class DBWorker(multiprocessing.Process):
    """
    Subclass implementation of multiprocessing that gets a tweet from
    the tweet queue, processes it, and puts in the the DB queue.
    """
    def __init__(self, tq, errq, countq, db_path=None):
        multiprocessing.Process.__init__(self)
        self.tweet_queue = tq
        self.errq        = errq
        self.countq      = countq
        self.count       = 0
        self.session     = None
        self.db_path     = db_path
        self.streamsession_id = None
        self.tweet_lookup_queue = None
        self.tweet_text_lookup_queue = None
        self.lookup_queue_limit = 100

        
    def run(self):
        print("starting DB Worker")

        qh = QueueHandler(self.errq)
        f = logging.Formatter('SW formatter: %(asctime)s: %(name)s|%(processName)s|%(process)d|%(levelname)s -- %(message)s')
        qh.setFormatter(f)
        qh.setLevel(logging.INFO)
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        self.log.propagate = False
        self.log.addHandler(qh)

        self.log.info('DBWorker {} starting'.format(self.pid))

        self.tweet_lookup_queue = {}
        self.tweet_text_lookup_queue = []

        while True:
            
            try:
                d = self.tweet_queue.get(block=True)
            except Empty:
                time.sleep(SLEEP_TIME)
            else:
                try:
                    code, data = d
                except ValueError:
                    self.log.exception('Code, data assignment failed with:\n{}\n'.format(d))
                else:
                    if code==TWEET_MESSAGE:
                        # Set streamsession_id from data
                        ssid = data.pop('streamsession_id', None)
                        if ssid is not None:
                            self.streamsession_id = ssid
                        
                        retries = 0
                        retry_limit = 5
                        while retries < retry_limit:
                            
                            try:
                                self.process_tweet(data)
    
                            except (IntegrityError, OperationalError) as e:
                                msg =  '\n\n' + '*'*70
                                msg += '\n\nDB ingegrity error. Retrying ({}).'.format(retries)
                                msg += 'Exception: {}\n'
                                msg += '-'*70 + '\n'
                                msg += traceback.format_exc()
                                msg += '\n\n{0}\nTweet Data:\n{1}\n{0}'.format('*'*70, json_dumps(data, indent=4))
                                
                                self.log.warning(msg)
                                retries += 1
    
                            else:
                                retries = retry_limit
    
                        # Check/dump lookup queues
                        if (len(self.tweet_lookup_queue) >=
                            self.lookup_queue_limit):
                            self.dump_tweet_lookup_queue()
                        if (len(self.tweet_text_lookup_queue) >=
                            self.lookup_queue_limit):
                            self.dump_tweet_text_lookup_queue()
                            
                        self.countq.put(1)
                        self.count += 1
    
                    elif code == START_MESSAGE: # stream started, time passed as data
                        self.log.debug('received START_MESSAGE')
                        session = get_session(self.db_path)
                        ss = session.merge(StreamSession(starttime=data))
                        self.commit_transaction(session)
                        self.streamsession_id = ss.id
                        session.close()
    
    
                    elif code == STOP_STREAM_MESSAGE: # stream stopped, time passed as data
                        self.log.debug('received STOP_STREAM_MESSAGE')
                        session = get_session(self.db_path)
                        ss = session.merge(StreamSession(id=self.streamsession_id))
                        ss.endtime=data
                        self.commit_transaction(session)
                        session.close()
    
                    elif code == STOP_MESSAGE: # process stopped by parent
                        # replace message for other workers
                        
                        self.tweet_queue.put((code, data))
                        print('stopping DB worker')
                        print('    dumping tweet lookup queue...')
                        self.dump_tweet_lookup_queue()
                        print('    DONE.')
                        print('    dumping tweet text lookup queue...')
                        self.dump_tweet_text_lookup_queue()
                        print('    DONE.')
                        print('Recording session stop time')
                        print('    DONE.')
                        break
                    
        print('{}: Process {} (id={}) finished.'.format(str(dt.now()),
                                                        self.name,
                                                        self.pid))

    def process_tweet(self, tweet): 
        """
        Takes tweet JSON from twitter API and returns a dict, where
        each key corresponds to a DB column.
        """
        if tweet is None:
            return

        # lower-case all keys
        tweet = {k.lower():v for k, v in tweet.items()}

        ###################
        # Delete messages #
        ###################
        try:
            delete_tw = tweet.pop('delete')

        except KeyError: # No delete message in tweet data -- do nothing
            pass

        except AttributeError: # tweet is not a dict (is None)
            self.log.exception('Tweet data has no .pop method. Tweet: {}'.format(tweet))

        else: # delete message retrieved
            self.log.info('Delete message received')
            
            # get status id from message
            try:
                delete_id_str = delete_tw['status']['id_str']

            except (KeyError, AttributeError): # None has no attribute 'get' or is missing key(s)
                self.log.info('No id_str availabe in  delete message: \n{}'.format(delete_tw))

            else: # retrieved status id from delete message
                session = get_session(self.db_path)

                try:
                    t = session.query(Tweet).get(delete_id_str)
                    t.deleted = True
                    self.commit_transaction(session)

                except AttributeError: # t is None -- id not in DB
                    session.rollback()
                    self.log.info('Unable to retrieve DB record for tweet (id_str = {}).'.format(delete_id_str))

                else: # Marked DB record successfully
                    self.log.info('Tweet (id_str = {}) marked for deletion'.format(delete_id_str))

                finally:
                    session.close()
            return # Stop


        ##################
        # Limit messages #
        ##################
        try:
            limit_msg = tweet.pop('limit')

        except KeyError: # No limit message in tweet data -- do nothing
            pass
        
        except AttributeError: # tweet is not a dict (is None)
            pass # log entry created above

        else: # limit message retrieved
            self.log.info('Limit message received: \n{}\n'.format(limit_msg))

            try:
                limit_val = limit_msg['track']

            except (KeyError, AttributeError): # limit_msg is not a dict
                self.log.info('No \'track\' entry in limit message.')

            else:
                session = get_session(self.db_path)
                
                try:
                    entry = session.merge(StreamSession(id=self.streamsession_id))
                    entry.limit = limit_val
                    self.commit_transaction(session)

                except Exception as e:
                    session.rollback()
                    self.log.warning('Error trying to update rate limiting data:\n' \
                                + '    streamsession_id={0}\n'\
                                + '    limit_val={1}\n' \
                                + '    Error: \n{2}\n'.format(
                                    self.streamsession_id,
                                    limit_val,
                                    e))
                else: # limit successfully written to DB
                    self.log.warning(
                        'Twitter rate limiting: {} tweets dropped.'.format(
                            limit_val
                        )
                    )                    
                finally:
                    session.close()
            return # stop

        # ensure tweet id is not none; if it is, stop
        try:
            tweet_id = tweet.pop('id_str')
        except (KeyError, AttributeError): # Tweet is None or does not have id_str
            err_text = '\n*** Error: Tweet has no ID. ***' + \
                       '\nTweet details:\n{}\n'.format(
                           json_dumps(tweet, indent=4))
            self.log.warning(err_text)
            return # stop
        else:
            self.log.debug('tweet id is {} in try-block scope'.format(tweet_id))
        self.log.debug('tweet id is {} outside try-block scope'.format(tweet_id))

        # Process RT status
        # Need to do this first so that id for reply tweet is in DB
        # before merge below
        try:
            tweet_retweet_status = tweet.pop("retweet_status")
        except KeyError:
            tweet_retweet_status = {}
        else:
            self.process_tweet(tweet_retweet_status)

        # Start session to begin DB transaction
        # Need to do this after the RT status is processed, but before
        # other properties are extracted from the data to be merged
        # with the DB data.
        session = get_session(self.db_path)

        # get id and merge tweet
        t = session.merge(Tweet(id_str=tweet_id))
        self.log.debug('Merged id (t.id_str) is {}'.format(t.id_str))
        self.log.debug('Initial __dict__ of tweet {0}:\n{1}\n'.format(
            t.id_str, t.__dict__))
            
        # Process tweet text
        try:
            tweet_text = tweet.pop("text")

        except KeyError: # No text element in dict
            self.log.warning(
                'No text found for tweet ({0}):\n{1}'.format(
                    tweet_id, json_dumps(tweet, indent=4)))
            
        else:
            self.log.debug('assigned text properties to tweet {}'.format(t.id_str))
            tb = TextBlob(tweet_text)
            t.sentence_count = len(tb.sentences)
            t.word_count = len(tb.words)
            t.tb_char_count = len(''.join(tb))
            t.char_count = len(tweet_text)
            t.sent_polarity = tb.sentiment.polarity
            t.sent_subjectivity = tb.sentiment.subjectivity

        self.log.debug('__dict__ of tweet {0} After adding text properties:\n{1}\n'.format(
            t.id_str, t.__dict__))

        # @TO-DO: sample tweet text for sentiment check

        # If tweet is a reply, load original from twitter and add to DB            
        try:
            reply_id_str = tweet['in_reply_to_status_id_str']
        except KeyError: # not a reply
            pass
        else: # it's a reply
            # add it to the queue
            if reply_id_str is not None:
                self.tweet_lookup_queue[reply_id_str] = self.tweet_lookup_queue.get(
                    reply_id_str, dt.now())

            # add to tweet's replied-to field
            self.log.debug('reply_id_str is {}'.format(reply_id_str))
            if reply_id_str is not None:
                t_reply = session.merge(Tweet(id_str=reply_id_str))
                t.in_reply_to = t_reply

        self.log.debug('__dict__ of tweet {0} After trying to add in_reply_to:\n{1}\n'.format(
            t.id_str, t.__dict__))


        # Add RT

        try:
            rt_status_id_str = tweet_retweet_status['id_str']
        except (KeyError, AttributeError): # No id_str key or is object is not a dict (None)
            pass
        else:
            if rt_status_id_str is not None:
                t.original = session.merge(Tweet(id_str=rt_status_id_str))
            
        self.log.debug('__dict__ of tweet {0} After adding original:\n{1}\n'.format(
            t.id_str, t.__dict__))
        
        # Time/tracking properties
        try:
            t.created_at = date_parser.parse(tweet['created_at'])
        except KeyError: # No 'created_at' attribute in dict
            pass
        t.captured_at = dt.now()
        
        self.log.debug('__dict__ of tweet {0} after adding captured_at:\n{1}\n'.format(
            t.id_str, t.__dict__))

        self.log.debug('adding streamsession_id={}'.format(self.streamsession_id))
        t.stream_session_id = self.streamsession_id

        self.log.debug('__dict__ of tweet {0} after adding stream_session:\n{1}\n'.format(
            t.id_str, t.__dict__))
        
        # Process Tweet User
        try:
            tweet_user = tweet.pop("user")

        except KeyError: # no tweet user
            pass
        
        else:
            if t.user is None: # tweet does not have a user in DB -- create the user, if necessary
                try:
                    uid = tweet_user['id_str']

                except KeyError: # no id_str in user data
                    pass

                else:
                    if uid is not None:
                        t.user = session.merge(User(id_str=uid))
                        
            if t.user is not None: # User was present or has been merged
                ## if t.user.screen_name is None: # user doesn't have screen name
                ##     try:
                ##         usn = tweet_user['screen_name']
    
                ##     except KeyError: # No screen_name in user data
                ##         pass

                ##     else:
                ##         if usn is not None:
                ##             t.user.screen_name = usn
        
                uprops_list = [
                    'screen_name',
                    'listed_count',
                    'statuses_count',
                    'favourites_count',
                    'followers_count',
                    'verified',
                    'default_profile_image',
                    'geo_enabled',
                    'friends_count'
                    ]
                    
                up = UserProps()
                up.captured_at = dt.now()
                for attr in uprops_list:
                    try:
                        setattr(up, attr, tweet_user[attr])
                    except KeyError: # attr not in tweet_user
                        pass
                    except AttributeError: # couldn't set attribute of up
                        log.exception('Error assigning value to user property: No such attribute ({})'.format(attr))
    
                # Add creation time to up. This is a special case because
                # the date must be parsed before it can be entered
                # in the DB
                try:
                    tu_ca = tweet_user['created_at']
                except KeyError: # no date
                    pass
                else:
                    if tu_ca is not None:
                        up.created_at = date_parser.parse(tu_ca)
    
                t.user.props.extend([up])
        
        # Process entities
        try:
            tweet_entities = tweet.pop('entities')
        except KeyError:
            pass
        else:
            for mention in tweet_entities['user_mentions']:
                try:
                    muid = mention['id_str']
                except KeyError:
                    pass
                else:
                    if muid is not None:
                        u = session.merge(User(id_str=muid))
                        try:
                            u.screen_name = mention['screen_name']
                        except KeyError:
                            pass
                        session.merge(Mention(
                            user_id=muid,
                            tweet_id=tweet_id
                            )
                        )
                    
        # re-merge tweet prior to committing
        #t = session.merge(t)
        
        # commit changes
        self.commit_transaction(session)
        session.close()

    def dump_tweet_text_lookup_queue(self):
        if len(self.tweet_text_lookup_queue) > 0:
            try:
                tweet_text_res = lookup_many('tweet_text', self.tweet_text_lookup_queue)
                # tw_text = tweet_text_lookup(tweet_id)
            except Exception as e:
                print('\n\n' + '*'*70)
                print('Error retrieving tweet text for sentiment checking')
                print('Tweet IDs: ', ', '.join(self.tweet_text_lookup_queue))
                print('-'*70)
                print('Exception:\n', e)
                print('*'*70 + '\n')
                self.log.exception(e)

            else:
                for tw in tweet_text_res:
                    self.session.merge(
                        SentimentCheck(
                            tweet_id=tw[0],
                            tweet_text=tw[1]
                            )
                        )
                try:
                    self.session.commit()
                except Exception as e:
                    self.log.exception(e)
                    self.session.rollback()
                else:
                    self.tweet_text_lookup_queue = []

    def dump_tweet_lookup_queue(self):
        if (len(self.tweet_lookup_queue) < 1 or
            self.tweet_lookup_queue is None):
            return

        # get list of tweet ids from queue
        q = list(set(self.tweet_lookup_queue.keys()))
        qlen = len(q)

        # Try to lookup tweet data from twitter
        try:
            tweet_res = lookup_many('statuses', q)

        # Catch all exceptions
        except Exception as e:
            print('\n\n' + '*'*70)
            print('Error retrieving queued statuses (replies, RTs, etc.)')
            print('Tweet IDs: ', ', '.join(q))
            print('-'*70)
            print('Exception:\n', e)
            print('*'*70 + '\n')
            self.log.exception('Error retrieving queued statuses (replies, RTs, etc.)')

        # If there's no exception, process the result from twitter
        else:
            
            # iterate through result from twitter & process each
            # tweet retrieved
            for tw in tweet_res:
                self.process_tweet(tw)
            
            # Get id_str from each of the results from twitter,
            # filtering out Nones.
            tweet_res_ids = [y for y in [x.get('id_str', None) for x in tweet_res] if y is not None]

            # Iterate through list of ids that were in the queue,
            # extracting those
            self.tweet_lookup_queue = {x:self.tweet_lookup_queue[x]
                                       for x in q if (x not in tweet_res_ids) and
                                       (x is not None)}

            # using list comprehension to ensure everything is string for json.dumps()
            qstr = json_dumps({str(k):str(v) for k, v in self.tweet_lookup_queue.items()},
                              sort_keys=True,
                              indent=4)
            
            self.log.info('Tweet lookup queue (len: {}) after fetching and filtering: \n{}\n'.format(
                len(self.tweet_lookup_queue), qstr))

            # If the number of items remaining in the lookup queue
            # is more than half the size limit for the queue, purge
            # the oldest half of the items remaining in the queue
            if len(self.tweet_lookup_queue) > self.lookup_queue_limit/2:
                # purge old items from queue
                ## sort queue keys by values
                to_remove = sorted(self.tweet_lookup_queue,
                                   key=self.tweet_lookup_queue.__getitem__)

                ## get first half of sorted keys
                to_remove = to_remove[0:len(to_remove)//2]

                ## filter out or delete those (oldest) keys
                self.tweet_lookup_queue = {twid: time for twid, time
                                           in self.tweet_lookup_queue.items()
                                           if twid not in to_remove}

                qstr = json_dumps({str(k):str(v) for k, v in self.tweet_lookup_queue.items()},
                                  sort_keys=True,
                                  indent=4)

            self.log.info('Tweet lookup queue (len: {}) after checking queue length/paring down: \n{}\n'.format(
                len(self.tweet_lookup_queue), qstr))


    def commit_transaction(self, session, retries=5):
        err = None
        for r in range(0, retries):
            try:
                session.commit()
            except Exception as e:
                err = e
                tb = traceback.format_exc()
                self.log.warning('{0}\nError committing DB transaction. Retrying ({1} of {2}).\n{0}\n{3}\n'.format('*'*70, r+1, retries, tb))
                if r == retries - 1:
                    raise
            else:
                err = None
                break
        if err is not None:
            self.log.error('{2}\n{0}\n{3}\n{1}\n{2}\n\n'.format(err, tb, '*'*70, '-'*70))
            session.rollback()
            
class QueueChurner(multiprocessing.Process):
    """
    Subclass implementation of multiprocessing that allows a
    FanTwython object to run in its own process.
    """
    def __init__(self, from_q, to_q):
        multiprocessing.Process.__init__(self)
        self.from_q = from_q
        self.to_q = to_q

    def churn_queue(self):
        while not self.from_q.empty():
            d = self.from_q.get()
            try:
                code, data = d
            except TypeError as te:
                self.to_q.put(d)
            # filter out stope messages
            else:
                if code == STOP_MESSAGE:
                    pass
                else:
                    self.to_q.put((code, data))

    def run(self):
        self.churn_queue()
        
##########################
# MISC UTILITY FUNCTIONS #
##########################

def status_lookup(ids):
    """
    Retrieve status(es) via Twitter REST API.
    @param ids: list of tweet ids
    Returns a status/tweet object for each id in input
    """
    ids = list(set(ids))
    len_ids = len(ids) # @DEBUG
    ids = ','.join(ids)
    tw = Twython(CREDENTIALS['APP_KEY'],
                 CREDENTIALS['APP_SECRET'],
                 CREDENTIALS['ACCESS_KEY'],
                 CREDENTIALS['ACCESS_SECRET'])
    res = tw.lookup_status(id=ids)

    return res

def tweet_text_lookup(ids):
    """
    Get text of multiple tweets from a list of tweet id strings.
    Returns a list of (id, text) tuples.
    """
    statuses = status_lookup(ids)
    res = []
    for s in statuses:
        tw_id = s.get('id_str')
        tw_text = s.get('text')
        if not (tw_id is None or tw_text is None):
            res.append((tw_id, tw_text))
    return res

def tt_lookup(id):
    """
    Get the text of a single tweet by id
    """
    status = status_lookup([id])
    status = status[0]
    return status['text']
    
def screen_name_lookup(screen_names):
    tw = Twython(CREDENTIALS['APP_KEY'],
                 CREDENTIALS['APP_SECRET'],
                 CREDENTIALS['ACCESS_KEY'],
                 CREDENTIALS['ACCESS_SECRET'])

    users = tw.lookup_user(screen_name=screen_names)
    return users

def lookup_many(function, args):
    # API allows 100 users per call

    fs = {'statuses':status_lookup,
          'screen_names':screen_name_lookup,
          'tweet_texts':tweet_text_lookup}

    if function not in fs:
        return None

    f = fs[function]

    max_length = 100
    
    segments = []

    # split up large inputs
    while len(args)>max_length:
        # split input
        head, args = (args[:max_length],
                      args[max_length:])
        # add segment to calls
        segments.append(head)

    # append remainder to calls
    segments.append(args)

    # make API calls
    res = []
    for s in segments:
        print('Calling {0} with {1} arguments'.format(str(f), len(s)))
        try:
            r = f(s)
        except TwythonError as e:
            raise(e)
        else:
            res += r
            
    return res
