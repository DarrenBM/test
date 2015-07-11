# Main module for tweet harvesting
#---------------------------------------------------------------------
# NOTES
# - Use Queue class to create multi-threading safe Queue 
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# @TO-DO:
#        - UI
#        - Add team to DB
#            - How do I get the account from the result?
#        - Sentiment analysis
#        - Support for multiple leagues
#        - Record team -- Recording type of tweet is a separate problem
#           - If the tweet is by the team account (user:id_str is that account's id), then associate with that team
#           - if the tweet is by the team account, mark as "by the team"
#           - if the tweet 
#        - Identify type of tweet
#            - original (by the team)
#                - user id_str is the team's account
#                - it's not a retweet
#            - Retweet (of the team's original tweet
#                - it's a retweet
#                - team is not the user id_str
#                - team is the user id_str of the retweet
#            - team retweet (retweet of someone else's tweet by the team)
#                - user id_str is the team
#                - tweet is a retweet
#            - other
#        - get game data
#        - look at streaming interface spec at https://twython.readthedocs.org/en/latest/api.html#twython.TwythonStreamer.disconnect
#            - additional constructor parameters
#            - error handling
#            - disconnecting
#            - on_timeout()
#       - add the query to the streamer object itself so that we can call a method with no parameters to start the stream
#             -
#       - modify fieldnames to contain filters for different objects
#       - modify database to support multiple teams/leagues, many-to-many mentions
#          - add views
#       - Add SBNation twitter accounts
#       - look at Queue module for creating a local stream buffer
#       - set up error logging using logging module
#       - Clean up settings import so that ALL settings are in the settings file and importable by from settings import *
#       - Handle other Twitter messages and add them to the message window
#---------------------------------------------------------------------

import multiprocessing
from fanworkers import (StreamWorker,
                        DBWorker,
                        tweet_text_lookup,
                        screen_name_lookup)
from faninterface import FanGUI

from fansettings import *
from credentials import CREDENTIALS
import sqlite3 as sqlite
from twython import Twython
import time

import os

def initialize_db(path):
    print('Initializing database...')
    # Ensure foreign keys are turned on
    con = sqlite.connect(path)
    cur = con.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')
    con.commit()
    con.close()
    
    # Ensure required tables are in place
    print('    Verifying tables...')
    base_sql = "CREATE TABLE IF NOT EXISTS {t} ({c});"
    # Use DB_TABLES_LIST to ensure proper order of table creation
    for table_name in DB_TABLES_LIST:
#        print(table_name) # @DEBUG
        # get spec for table
        spec = DB_SPEC.get(table_name, None)

        # Check whether columns are specified for the table
        # spec is not defined -- all columns are None
        if spec is None:
            primary_key = None
            indexes = None
            fields = None
            foreign_keys = None
        # spec is defined. Retrieve column specs from spec.
        else:
            primary_key = spec.get('primary_key', None)
            indexes = spec.get('indexes', None)
            fields = spec.get('fields', None)
            foreign_keys = spec.get('foreign_keys', None)

#        print('Primary key: ', primary_key) # @DEBUG
#        print('Indexes: ', str(indexes)) # @DEBUG
#        print('Fields: ', str(fields)) # @DEBUG
#        print('Foreign Keys: ', str(foreign_keys)) # @DEBUG
        
        # patterns for DB field types in spec
        primary_key_pattern    = '{f} {dt} PRIMARY KEY'
        index_pattern          = '{f} {dt} UNIQUE'
        field_pattern          = '{f} {dt}'
        foreign_keys_pattern   = 'FOREIGN KEY({f}) REFERENCES {rt}({rc})'
        mc_primary_key_pattern = 'PRIMARY KEY ({fs})'
        mc_index_pattern       = 'CREATE UNIQUE INDEX IF NOT EXISTS {n} ON {t} ({cols});'

        # initialize containers for SQL for columns
        sql_arr = []
        foreign_keys_sql_arr = []
        mc_primary_key_arr = []
        more_sql_arr = []

        # generate SQL for primary key, if specified (single value)
        if primary_key is not None:
            if len(primary_key) == 1:
#           	 print('Primary key: ', primary_key) # @DEBUG
            	# Get datatype, default to 'TEXT'
            	dtype = DB_DATATYPES.get(primary_key[0], 'TEXT')
            	
            	# Make everything in DB lower case
            	primary_key = primary_key[0].lower()
            	
            	# Format SQL and append to SQL container
            	sql_arr.append(primary_key_pattern.format(f=primary_key,
                                                          dt=dtype))
            elif len(primary_key) > 1:
                # primary key is multi-column
                fs = ','.join(primary_key)
                mc_primary_key_arr.append(
                    mc_primary_key_pattern.format(fs=fs)
                    )

        # generate SQL for indexes, if specified (possibly multiple)
        if indexes is not None:
            # loop through indexed columns
            for ind, fs in indexes.items():
                #print('index: ', ind)  # @DEBUG
                # check whether index refers to fields
                if fs is None:
                    # ordinary index
                    # Get datatype, default to 'TEXT'
                    dtype = DB_DATATYPES.get(ind, 'TEXT')

                    # Make everything lower case
                    ind = ind.lower()
                
                    # Format SQL, append to SQL container
                    sql_arr.append(index_pattern.format(f=ind, dt=dtype))
                else:
                    # index refers to existing column(s)
                    sql = mc_index_pattern.format(n=ind, t=table_name, cols=','.join(fs))
                    more_sql_arr.append(sql)
                    
        # Generate SQL for fields, if specified (possibly multiple)
        if fields is not None:
            # Loop through fields
            for field in fields:
#                print('field: ', field) # @DEBUG
                # Get datatype, default to 'TEXT'
                dtype = DB_DATATYPES.get(field, 'TEXT')

                # Lower case
                field = field.lower()

                # format SQL, append to container
                sql_arr.append(field_pattern.format(f=field, dt=dtype))
	
        # Generate SQL for foreign keys, if specified (possibly multiple)
        if foreign_keys is not None:
            # Loop though foreign keys
            for field, params in foreign_keys.items():
                # get referred table from column spec
                ref_table = params.get('refers_to_table', None)

                # get referred column from column spec
                ref_col = params.get('refers_to_column', None)
#                print(' '.join(['foreign key:', field, '->(',ref_table,',',ref_col,')']))  # @DEBUG
                # Get datatype, default to 'TEXT'
                dtype = DB_DATATYPES.get(field, 'TEXT')

                # lower case
                field = field.lower()
                ref_table = ref_table.lower()
                ref_col = ref_col.lower()
                
                # Format SQL, depending on whether referred to column was fully specified
                # In all cases, create the column
                sql_arr.append(field_pattern.format(f=field, dt=dtype))                

                # Referred-to column was fully specified --
                # Add SQL for foreign key
                if (ref_table is not None) and (ref_col is not None): # @TO-DO: should probably raise an error here
                    foreign_keys_sql_arr.append(foreign_keys_pattern.format(f=field,
                                                               rt=ref_table,
                                                               rc=ref_col))
                else:
                    # Referred to column not fully specified --
                    # do nothing more
                    pass
        # combine SQL for foreign keys with other fields
        sql_arr = sql_arr + foreign_keys_sql_arr
        
        # Join SQL specification of columns for this table
        cols_spec = ', '.join(sql_arr)

        # Create complete SQL from base SQL patter, columns SQL, and table name
        sql = base_sql.format(t=table_name, c=cols_spec)      

#        print('SQL: ', sql) # @DEBUG
        # Connect to DB
        con = sqlite.connect(path)
        cur = con.cursor()

        try:
#            print('executing SQL for ' + table_name) # @DEBUG
            cur.execute(sql)
            for stmt in more_sql_arr:
                cur.execute(stmt)
            con.commit()
        except Exception as e:
            print("Error ensuring existence of necessary table")
            print(sql)
            con.rollback()
            raise e
        finally:
#            print('closing DB connection') # @DEBUG
            con.close()
        con.close()

    #----------------------------------
    # Ensure Teams are populated in DB 
    #----------------------------------
    print('    Populating teams...')
    # Connect to DB
    con = sqlite.connect(path)
    cur = con.cursor()

    # Base SQL for adding team (if not in DB)
    team_sql = 'INSERT OR REPLACE INTO teams(team_name, league) VALUES(?, ?);'

    # Make a copy of ACCOUNTS
    acct_table = list(ACCOUNTS)

    # make everything in accounts table lower case
    acct_table = [[(None if s is None else s.lower()) for s in acc] for acc in acct_table]
#    print('{0}\nLower case account table:\n{1}\n{0}\n'.format('*'*70, acct_table)) # @DEBUG
            
    
    # Iterate over teams
    for t in acct_table:
        # Ensure account is official/team account
#        print(str(t)) # @DEBUG
        if t[INDEX_TYPE] == 'official':
        # Get team name and cluster (league) for each team (lower case)
            name = t[INDEX_NAME]
            if name is not None:
                name=name.lower()
            cluster = t[INDEX_CLUSTER]
            if cluster is not None:
                cluster = cluster.lower()
                
            try:
                # Execute SQL with team name and cluster (league)
                cur.execute(team_sql, (name, cluster))
#                print('added team = {t}, cluster = {c}'.format(t=name, c=cluster)) # @DEBUG
            except Exception as e:
                # Print name and cluster that cause exception
                print('handling {t}, {c}'.format(t=name, c=cluster))
                raise

    # Commit all team additions to the DB
    con.commit()

    print('    Verifying accounts table...')
    # Base SQL for adding accounts to DB
    account_sql = 'INSERT OR REPLACE INTO accounts(id_str, cluster, type, screen_name, team_name, description) VALUES(?, ?, ?, ?, ?, ?);'

    # fill in missing ids
    ## collect missing accounts
    print('        Collecting account without IDs...')
    missing = []
    for acc in acct_table:
        if acc[INDEX_ID] is None:
            missing.append(acc[INDEX_SCREEN_NAME])

    # Query for screen names
    print('        Querying Twitter for missing IDs...')
    missing_users = screen_name_lookup(missing)
    missing_accts = {u.get('screen_name'):u.get('id_str') for u in missing_users}
    missing_reverse = {val:key for key, val in missing_accts.items()}

    # put results from twitter into the original table
    for acc in acct_table:
        if acc[INDEX_SCREEN_NAME] in missing_accts.keys():
            acc[INDEX_ID] = missing_accts.get(acc[INDEX_SCREEN_NAME])
#            print('{}\n>>> {} is in missing_accts.keys as {}\n{}'.format('*'*70,
#                                                                         acc[INDEX_SCREEN_NAME],
#                                                                         missing_reverse.get(acc[INDEX_ID]),
#                                                                         '*'*70)) #@DEBUG

#    print('{}\nAccounts filled with Twitter data:\n{}'.format('*'*70,'*'*70)) # @DEBUG
#    for acc in acct_table: # @DEBUG
#        print(acc)
#    print('*'*70 + '\n\n')
    
    # iterate over accounts
    print('        Inserting missing accounts...')
    for acc in acct_table:
        # Get data from settings for account
        id_str = acc[INDEX_ID]
        cluster = acc[INDEX_CLUSTER]
        acc_type = acc[INDEX_TYPE]
        screen_name = acc[INDEX_SCREEN_NAME]
        name = acc[INDEX_NAME]
        description = acc[INDEX_DESCRIPTION]
        try:
            # Execute SQL to add account to DB
            cur.execute(account_sql, (id_str, cluster, acc_type, screen_name, name, description))
#            print('Added account: id={i}, cluster={c}, type={at}, screen_name={sn}, team={tn}, description={d}'.format(i=id_str, c=cluster, at=acc_type, sn=screen_name, tn=name, d=description)) # @DEBUG
        except Exception as e:
            # print data that caused exception
            print('handling: ')
            print('    id_str: ', id_str)
            print('    cluster: ', cluster)
            print('    type: ', acc_type)
            print('    screen_name:', screen_name)
            print('    name: ', name)
            print('    description: ', description)
            raise

    # Commit all account additions to DB
    con.commit()
    con.close()

    populate_account_ids(path)

    create_views(path)

def populate_account_ids(path):
    print('\nPopulating empty account ids...')
    # connect to DB
    con = sqlite.connect(path)
    cur = con.cursor()

    # Query DB for list of all accounts
    cur.execute('SELECT id_str, screen_name FROM accounts;')
    accts = cur.fetchall()

#    print('\nAll {} Accounts Fetched:\n{}\n'.format(len(accts), accts)) # @DEBUG
    # filter for accounts without an id
    scr_names = [x[1] for x in accts if (x[0] is None or x[0] =='')]

#    print('\n{} empty screen names from DB:\n{}\n'.format(len(scr_names), scr_names)) # @DEBUG

    # fetch users from Twitter
    users = screen_name_lookup(scr_names)

    # get (id, screen name) for each user. Make screen names lower case
    updates = [[u.get('id_str'), u.get('screen_name')] for u in users]

    # Make screen names lower case, make tuples
    updates = [(x[0], x[1].lower()) for x in updates]

#    print('List of {} updates to make: \n{}'.format(len(updates), updates)) # @DEBUG
    # update database. use COLLATE NOCASE to ensure that match is case-insensitive
    sql = "UPDATE accounts SET id_str=? WHERE screen_name=? COLLATE NOCASE;"
    for ud in updates:
#        print('Updating DB with:\n    Query: {}\n    Data: {}'.format(sql, ud)) # @DEBUG
        cur.execute(sql, ud)
        con.commit()
    con.close()
#    print('Updated {} accounts.\n'.format(len(scr_names))) # @DEBUG

def create_views(path):
#    print('\n\n{}\nCreating views:\n'.format('*'*70)) # @DEBUG
    con=sqlite.connect(path)
    cur = con.cursor()
    for view in DB_VIEWS:
        sql = 'CREATE VIEW IF NOT EXISTS {} AS {}'.format(view[0],view[1])
        cur.execute(sql)
#        print('{}\nCreated view {} with \n    SQL: {}'.format('-'*70, view[1], view[0])) # @DEBUG
    con.commit()
    con.close()
    
if __name__ == '__main__':

    # do file structure checks
    # initialize/update database
    # Check directory structure

    # Initialize Database
    initialize_db()
    
    # connect to DB
    con = sqlite.connect(DB_PATH)
    cur = con.cursor()

    # Query DB for list of accounts
    cur.execute('SELECT id_str, screen_name FROM accounts;')

    accounts = cur.fetchall()
    accounts = [(x[0], x[1]) for x in accounts]

    # check for empty accounts
    for acc in accounts:
        if acc[0] is None:
            print('\n' + ('*'*70))
            print('Missing screen_name in accounts')
            acc_list = screen_name_lookup([acc[1]])
            acc_id = acc_list[0].get('id_str', None)

            # update DB with account id
            d = (acc_id, acc[1])
            sql = 'UPDATE accounts SET id_str=? WHERE screen_name=?'
            print('Updating database with:')
            print('    SQL: ', sql)
            print('    data:', d)
            cur.execute(sql, d)
            con.commit()

    # Get list of account ids from DB
    cur.execute('SELECT id_str FROM accounts;')
    account_ids = cur.fetchall()
    account_ids = [x[0] for x in account_ids]
    
    con.close()

    print('\n\n*************** ACCOUNT IDS***********')
    print(account_ids)

    # queues for passing data among processes
    stream_q = multiprocessing.Queue()
    db_q = multiprocessing.Queue()
    msg_q = multiprocessing.Queue()
        
    # create new stream worker with ids from accounts
    sw = StreamWorker(stream_q,
                      msg_q,
                      follow=','.join(account_ids)) #removed for testing

    ##### testing code ###############################
    pw = ProcessWorker(stream_q, db_q)               #
    dbw = DBWorker(db_q, DB_PATH, 'tweets', DB_SPEC) #
    sw.start()                                       #
    pw.start()                                       #
    dbw.start()                                      #
    ##################################################
    
    # print queue lengths
    while (True):
        print('\n' + '*'*70)
        print('Stream Queue Length: ', stream_q.qsize())
        print('DB Queue Length: ', db_q.qsize())
        time.sleep(5)
    # create interface

    # start  stream worker
    # start process worker(s)
    # start db worker(s)

    # set up conditions for stopping process (e.g., stop all processes
    # if some continuation variable == False
    


