# @TO-DO: Add an array variable to GUI object to hold stream durations and append stream time when stream is restarted.
#           * Update cumulative stream time by summing array and adding current duration.
#           * Reset the array when streaming is manually stopped
#         Add backup settings to GUI
#           * Add size limit
#           * Add timer interval
#         Add cycling of objects (to try to address some of the apparent slowing)
#           * objects to cycle: SWs, PWs, DBWs, FanGUI (?), TQ, DBQ, ErrQ, MsgQ
#           * Steps:
#              * Create new Queues
#              * Create new Workers
#              * Start new workers w/ new queues
#              * Stop old workers
#              * transfer any contents of old Qs to new ones
#         Add streamsession ID(s) id to GUI
#     !!! Add email alerts for errors !!!

# Imports
from fanlogconfig import getFanLog, LOGGING

## Interface
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import *
import tkinter.messagebox as msgbox

## Processing
import multiprocessing

## Utilities
import shutil
from random import randint # for testing simulations
from datetime import datetime as dt
from datetime import timedelta as td
import re
import traceback

## Fan libs
from db_spec import *
from fanworkers import *
from fansettings import *
import fantwitter as ft


class FanGUI(object):
    """
    Subclass implementation of multiprocessing that provides a graphical
    interface for tweet streaming
    """
    def __init__(self, num_sws=1, num_pws=1, num_dbws=1):


        # get log, queuelistener, and queue using getFanLog
        # Log, etc., must be created during GUI initialization;
        # otherwise, rotating the log file will raise an error,
        # apparently because the file is in use by two process at the
        # same time.
        self.log, self.ql, self.errq = getFanLog(LOGGING)
        self.ql.start()
        
        #____Streaming setup__________________________________________

        # counters
        self.rate_smoothing = 50
        self.q_smoothing = 5
        self.tweet_count=0
        self.twq_sizes = [0 for x in range(0, self.q_smoothing)]
        self.db_count=0 
        self.err_count=0
        self.rates = [(0,dt.now()) for x in range(0, self.rate_smoothing)]

        # timers
        self.start_time = None
        self.time_elapsed = td(0)

        # Query parameters
        self.follow = None
        self.track = None
        self.stream_params = None
        
        # Flag to stop/continue streaming -- Not streaming at start, so False
        self.streaming = False

        # DB
        self.db_path = None 
        ## set db_path to most recent db file
        self.load_current_db_file()
        self.db_path += '_test' # @DEBUG

        # Backups
        self.backup_interval = td(hours=DB_BACKUP_INTERVAL)
        self.next_backup_time = dt.now() + self.backup_interval
        self.db_file_size_limit = DB_FILE_SIZE_LIMIT
        if os.path.isfile(self.db_path):
            self.db_file_size = os.stat(self.db_path).st_size/(1024**2)
        else:
            self.db_file_size = 0 # Can't get file size now because file doesn't exist

        # Capturing/cleaning up old processes
        self.procs_used = []

        #____Interface Layout_______________________________________
        
        # initialize root
        self.root = Tk()
        self.root.title('Fan Streamer')
        #self.root.geometry('350x300+300+300')
        self.root.protocol('WM_DELETE_WINDOW', self.window_close)

        # worker counts
        ## Note: IntVar() instances must be declared after self.root
        ##       because they attach to the active Tk() instance
        self.num_sws = IntVar()
        self.num_sws.set(1)
        self.num_pws = IntVar()
        self.num_pws.set(0)
        self.num_dbws = IntVar()
        self.num_dbws.set(1)

        # Workers (placeholders)
        self.dbws = []
        self.sws = []

        # Chunk size
        self.chunk_size = IntVar()
        self.chunk_size.set(1024)

        # Initialize main content frame
        self.mainframe = Frame(self.root)
        self.style = Style()
        self.mainframe.style = self.style
        self.mainframe.style.theme_use('default')
        self.mainframe.pack(fill=BOTH, expand=1)
        

        #-------------------------------------------------------------
        # Formatting constants
        #-------------------------------------------------------------
        
        region_padding = 5
        button_padding = 3


        #-------------------------------------------------------------
        # Header Region
        #-------------------------------------------------------------

        self.style.configure('header.TFrame', background='#555')
        self.header_frame = Frame(self.mainframe, style='header.TFrame')
        self.header_frame.pack(fill=BOTH,
                               padx=region_padding,
                               pady=region_padding
                               )

        # Allow first col to expand
        self.header_frame.columnconfigure(0, weight=1)

        # button to start/stop stream. Bind to toggle_stream()
        self.stream_btn = Button(self.header_frame,
                                 command=self.toggle_stream
                                 )
        self.stream_btn.configure(text='Start Streaming')
        self.stream_btn.grid(row=0,
                             column=0,
                             padx=button_padding,
                             pady=button_padding,
                             sticky=E
                             )

        # button for manually archiving db
        self.archive_db_btn = Button(self.header_frame,
                                     command=self.archive_db
                                     )
        self.archive_db_btn.configure(text='Archive DB')
        self.archive_db_btn.grid(row=0,
                                 padx=button_padding,
                                 pady=button_padding,
                                 column=2,
                                 sticky=E
                                 )


        #-------------------------------------------------------------
        # Worker Settings Region
        #-------------------------------------------------------------
        self.worker_frame = Frame(self.mainframe)
        self.worker_frame.pack(fill=BOTH,
                               expand=0,
                               padx=region_padding,
                               pady=region_padding
                               )

        # Worker fields label
        self.workers_lab = Label(self.worker_frame,
                                 text='Number of worker processes:',
                                 justify=LEFT,
                                 font=('Helvetica',8,'bold'),
                                 anchor=N
                                 )
        self.workers_lab.grid(row=0,
                              column=0,
                              columnspan=4,
                              sticky=S+W
                              )
        
        # Stream Workers
        ## Label
        self.streamworkers_lab = Label(self.worker_frame,
                                       text='Stream workers:',
                                       justify=LEFT,
                                       font=('Helvetica', 8, 'normal'),
                                       anchor=N
                                       )
        self.streamworkers_lab.grid(row=1,
                                    column=0,
                                    sticky=N+E
                                    )
        ## Data
        self.streamworkers_dat = Entry(self.worker_frame,
                                       width=4,
                                       textvariable=self.num_sws
                                       )
        self.streamworkers_dat.grid(row=1,
                                    column=1,
                                    sticky=N+W
                                    )

        
        # Process Workers
        ## Label
        self.processworkers_lab = Label(self.worker_frame,
                                        text='Process workers:',
                                        justify=LEFT,
                                        font=('Helvetica', 8, 'normal'),
                                        anchor=N
                                        )
        self.processworkers_lab.grid(row=1,
                                     column=2,
                                     sticky=N+E
                                     )
        ## Data
        self.processworkers_dat = Entry(self.worker_frame,
                                        width=4,
                                        textvariable=self.num_pws
                                        )
        self.processworkers_dat.grid(row=1,
                                     column=3,
                                     sticky=N+W
                                     )

        # DB Workers
        ## Label
        self.dbworkers_lab = Label(self.worker_frame,
                                   text='DB workers:',
                                   justify=LEFT,
                                   font=('Helvetica', 8, 'normal'),
                                   anchor=N
                                   )
        self.dbworkers_lab.grid(row=1,
                                column=4,
                                sticky=N+E
                                )
        ## Data
        self.dbworkers_dat = Entry(self.worker_frame,
                                   width=4,
                                   textvariable=self.num_dbws
                                   )
        self.dbworkers_dat.grid(row=1,
                                column=5,
                                sticky=N+W
                                )

        # Chunk size fields label
        self.chunk_lab = Label(self.worker_frame,
                               text='Chunk size for streamer(s):',
                               justify=LEFT,
                               font=('Helvetica',8,'bold'),
                               anchor=N+W
                               )
        self.chunk_lab.grid(row=0,
                            column=6,
                            columnspan=2,
                            sticky=E+W
                            )

        ## Label
        self.chunksize_lab = Label(self.worker_frame,
                                   text='Chunk size:',
                                   justify=LEFT,
                                   font=('Helvetica', 8, 'normal'),
                                   anchor=N+W
                                   )
        self.chunksize_lab.grid(row=1,
                                column=6,
                                sticky=E+W
                                )
        ## Data
        self.chunksize_dat = Entry(self.worker_frame,
                                   width=6,
                                   textvariable=self.chunk_size
                                   )
        self.chunksize_dat.grid(row=1,
                                column=7,
                                sticky=E+W
                                )


        #-------------------------------------------------------------
        # Stream Query Region
        #-------------------------------------------------------------
        
        self.query_frame = Frame(self.mainframe)
        self.query_frame.pack(fill=BOTH,
                              expand=1,
                              padx=region_padding,
                              pady=region_padding
                              )

        # Allow follow box to expand vertically
        self.query_frame.rowconfigure(0, weight=1)

        # Allow track box to expand vertically
        self.query_frame.rowconfigure(3, weight=1)

        # Allow Follow and Track boxes to expand horizontally
        self.query_frame.columnconfigure(6, weight=1)
        
        # Query display
        ## Follow
        ### Label
        self.follow_lab = Label(self.query_frame,
                                text='Follow:',
                                justify=LEFT,
                                font=('Helvetica', 8, 'bold'),
                                anchor=N
                                )
        self.follow_lab.grid(row=0,
                             column=0,
                             sticky=N+E
                             )

        ## Data
        self.follow_dat = ScrolledText(master=self.query_frame,
                                       wrap=WORD,
                                       height=5
                                       )
        if (self.follow is not None):
            self.follow_dat.insert(INSERT, self.follow_text)
        self.follow_dat.grid(row=0,
                             column=1,
                             columnspan=6,
                             padx=3,
                             sticky=N+S+E+W
                             )

        ## Track
        ### Label
        self.track_lab = Label(self.query_frame,
                               text='Track:',
                               justify=LEFT,
                               font=('Helvetica', 8, 'bold'),
                               )
        self.track_lab.grid(row=3,
                            column=0,
                            sticky=N+E,
                            )

        ## Data
        self.track_dat = ScrolledText(master=self.query_frame,
                                      wrap=WORD,
                                      height=5,
                                      )
        if self.track is not None:
            self.track_dat.insert(INSERT, self.track)
        else:
            self.track_dat.insert(INSERT, 'NFL,NBA,NHL,MLB')
        self.track_dat.grid(row=3,
                            rowspan=1,
                            column=1,
                            columnspan=6,
                            padx=3,
                            sticky=N+S+E+W
                            )

        # Follow/account selectors
        self.follow_selectors = {}
        ## MLB
        ### Official
        self.mlb_official_var = BooleanVar()
        self.mlb_official_var.set(True)
        self.mlb_official_check = Checkbutton(
            self.query_frame,
            text='MLB Official',
            variable=self.mlb_official_var,
            onvalue=True,
            offvalue=False,
            command=lambda:self.set_follow_selector(
                'mlb',
                ('mlb', 'official', self.mlb_official_var.get())
            )
        )
        self.mlb_official_check.grid(row=1,
                                     column=1,
                                     sticky=W
                                     )
        self.set_follow_selector('mlb',('mlb', 'official', self.mlb_official_var.get()))

        ### Blog
        self.mlb_blog_var = BooleanVar()
        self.mlb_blog_var.set(True)
        self.mlb_blog_check = Checkbutton(
            self.query_frame,
            text='MLB Blog',
            variable=self.mlb_blog_var,
            onvalue=True,
            offvalue=False,
            command=lambda:self.set_follow_selector(
                'mlb_blog',
                ('mlb', 'blog', self.mlb_blog_var.get())
            )
        )
        self.mlb_blog_check.grid(row=2,
                                 column=1,
                                 sticky=W
                                 )
        self.set_follow_selector('mlb',
                                 ('mlb', 'blog', self.mlb_blog_var.get())
                                 )

        ## NBA
        ### Official
        self.nba_official_var = BooleanVar()
        self.nba_official_var.set(True)
        self.nba_official_check = Checkbutton(
            self.query_frame,
            text='NBA Official',
            variable=self.nba_official_var,
            onvalue=True,
            offvalue=False,
            command=lambda:self.set_follow_selector(
                'nba',
                ('nba', 'official', self.nba_official_var.get())
            )
        )
        self.nba_official_check.grid(row=1,
                                     column=2,
                                     sticky=W
                                     )
        self.set_follow_selector('nba',
                                 ('nba', 'official', self.nba_official_var.get())
                                 )

        ### Blog
        self.nba_blog_var = BooleanVar()
        self.nba_blog_var.set(True)
        self.nba_blog_check = Checkbutton(
            self.query_frame,
            text='NBA Blog',
            variable=self.nba_blog_var,
            onvalue=True,
            offvalue=False,
            command=lambda:self.set_follow_selector(
                'nba_blog',
                ('nba', 'blog', self.nba_blog_var.get())
            )
        )
        self.nba_blog_check.grid(row=2,
                                 column=2,
                                 sticky=W
                                 )
        self.set_follow_selector('nba',
                                 ('nba', 'blog', self.nba_blog_var.get())
                                 )

        ## NFL
        ### Official
        self.nfl_official_var = BooleanVar()
        self.nfl_official_var.set(True)
        self.nfl_official_check = Checkbutton(
            self.query_frame,
            text='NFL Official',
            variable=self.nfl_official_var,
            onvalue=True,
            offvalue=False,
            command=lambda:self.set_follow_selector(
                'nfl',
                ('nfl', 'official', self.nfl_official_var.get())
            )
        )
        self.nfl_official_check.grid(row=1,
                                     column=3,
                                     sticky=W
                                     )
        self.set_follow_selector('nfl',
                                 ('nfl', 'official', self.nfl_official_var.get())
                                 )

        ### Blog
        self.nfl_blog_var = BooleanVar()
        self.nfl_blog_var.set(True)
        self.nfl_blog_check = Checkbutton(
            self.query_frame,
            text='NFL Blog',
            variable=self.nfl_blog_var,
            onvalue=True,
            offvalue=False,
            command=lambda:self.set_follow_selector(
                'nfl_blog',
                ('nfl', 'blog', self.nfl_blog_var.get())
            )
        )
        self.nfl_blog_check.grid(row=2,
                                 column=3,
                                 sticky=W
                                 )
        self.set_follow_selector('nfl',
                                 ('nfl', 'blog', self.nfl_blog_var.get())
                                 )

        ## NHL
        ### Official
        self.nhl_official_var = BooleanVar()
        self.nhl_official_var.set(True)
        self.nhl_official_check = Checkbutton(
            self.query_frame,
            text='NHL Official',
            variable=self.nhl_official_var,
            onvalue=True,
            offvalue=False,
            command=lambda:self.set_follow_selector(
                'nhl',
                ('nhl', 'official', self.nhl_official_var.get())
            )
        )
        self.nhl_official_check.grid(row=1,
                                     column=4,
                                     sticky=W
                                     )
        self.set_follow_selector('nhl',
                                 ('nhl', 'official', self.nhl_official_var.get())
                                 )

        ### Blog
        self.nhl_blog_var = BooleanVar()
        self.nhl_blog_var.set(True)
        self.nhl_blog_check = Checkbutton(
            self.query_frame,
            text='NHL Blog',
            variable=self.nhl_blog_var,
            onvalue=True,
            offvalue=False,
            command=lambda:self.set_follow_selector(
                'nhl_blog',
                ('nhl', 'blog', self.nhl_blog_var.get())
            )
        )
        self.nhl_blog_check.grid(row=2,
                                 column=4,
                                 sticky=W
                                 )
        self.set_follow_selector('nhl',
                                 ('nhl', 'blog', self.nhl_blog_var.get())
                                 )

        ## Buttons
        ### Load follow from checkbuttons
        self.load_follow_btn = Button(self.query_frame,
                                command=self.load_follow)
        self.load_follow_btn.configure(text='Load')
        self.load_follow_btn.grid(row=1,
                                  padx=button_padding,
                                  pady=button_padding,
                                  column=5,
                                  sticky=W
                                  )

        ### clear follow
        self.clear_follow_btn = Button(self.query_frame,
                                       command=self.clear_follow
                                       )
        self.clear_follow_btn.configure(text='Clear')
        self.clear_follow_btn.grid(row=2,
                                   padx=button_padding,
                                   pady=button_padding,
                                   column=5,
                                   sticky=W
                                   )

        # Load follow to begin
        self.load_follow()
        

        #-------------------------------------------------------------
        # Info Region
        #-------------------------------------------------------------

        self.info_frame = Frame(self.mainframe)
        self.info_frame.pack(fill=BOTH,
                             padx=region_padding,
                             pady=region_padding,
                             expand=0,
                             )

        # Tweet queue display
        ## Label
        self.tq_lab = Label(self.info_frame,
                            text='Tweet Q Size: ',
                            justify=RIGHT,
                            anchor=NE,
                            )
        self.tq_lab.grid(row=0,
                         column=0,
                         sticky=E+W)

        ## Data
        self.tq_dat_text = StringVar()
        self.tq_dat = Label(self.info_frame,
                            textvariable=self.tq_dat_text,
                            justify=RIGHT,
                            width=10,
                            anchor=NE,
                            relief=RIDGE
                            )
        self.tq_dat_text.set('0')
        self.tq_dat.grid(row=0,
                         column=1,
                         padx=4,
                         sticky=W
                         )

        # DB queue display 
        ## Label
        self.dbq_lab = Label(self.info_frame,
                            text='DB Q Size: ',
                            justify=RIGHT,
                            anchor=NE,
                            )
        self.dbq_lab.grid(row=1,
                          column=0,
                          sticky=E+W
                          )

        ## Data
        self.dbq_dat_text = StringVar()
        self.dbq_dat = Label(self.info_frame,
                             textvariable=self.dbq_dat_text,
                             justify=LEFT,
                             width=10,
                             anchor=NE,
                             relief=RIDGE
                             )
        self.dbq_dat_text.set('0')
        self.dbq_dat.grid(row=1,
                          column=1,
                          padx=4,
                          sticky=W
                          )

        # Tweets processed count display
        ## Label
        self.tweet_count_lab = Label(self.info_frame,
                                     text='Tweets Received: ',
                                     justify=RIGHT,
                                     anchor=NE,
                                     )
        self.tweet_count_lab.grid(row=0,
                                  column=2,
                                  sticky=E+W
                                  )

        ## Data
        self.tweet_count_dat_text = StringVar()
        self.tweet_count_dat = Label(self.info_frame,
                                     textvariable=self.tweet_count_dat_text,
                                     justify=LEFT,
                                     anchor=NE,
                                     relief=RIDGE,
                                     width=10
                                     )
        self.tweet_count_dat_text.set('0')
        self.tweet_count_dat.grid(row=0,
                                  column=3,
                                  padx=4,
                                  sticky=W
                                  )

        # DB jobs processed count display
        ## Label
        self.db_count_lab = Label(self.info_frame,
                                  text='DB queries: ',
                                  justify=RIGHT,
                                  anchor=NE,
                                  )
        self.db_count_lab.grid(row=1,
                               column=2,
                               sticky=E+W
                               )

        ## Data
        self.db_count_dat_text = StringVar()
        self.db_count_dat = Label(self.info_frame,
                                  textvariable=self.db_count_dat_text,
                                  justify=LEFT,
                                  anchor=NE,
                                  relief=RIDGE,
                                  width=10
                                  )
        self.db_count_dat_text.set('0')
        self.db_count_dat.grid(row=1,
                               column=3,
                               padx=4,
                               sticky=W
                               )

        # Stream elapsed time display
        ## Label
        self.time_elapsed_lab = Label(self.info_frame,
                                      text = 'Time Elapsed: ',
                                      justify=RIGHT,
                                      anchor=NE,
                                      )
        self.time_elapsed_lab.grid(row=0,
                                   column=5,
                                   sticky=E+W
                                   )

        ## Data
        self.time_elapsed_dat_text = StringVar()
        self.time_elapsed_dat = Label(self.info_frame,
                                      textvariable=self.time_elapsed_dat_text,
                                      justify=LEFT,
                                      anchor=NE,
                                      relief=RIDGE,
                                      width=10
                                      )
        self.time_elapsed_dat_text.set('00:00:00')
        self.time_elapsed_dat.grid(row=0,
                                   column=6,
                                   padx=4,
                                   sticky=W
                                   )

        # Error count display
        ## Label
        self.err_count_lab = Label(self.info_frame,
                                   text = 'Errors: ',
                                   justify=RIGHT,
                                   anchor=NE,
                                   )
        self.err_count_lab.grid(row=1,
                                column=5,
                                sticky=E+W
                                )

        ## Data
        self.err_count_dat_text = StringVar()
        self.err_count_dat = Label(self.info_frame,
                                   textvariable=self.err_count_dat_text,
                                   justify=LEFT,
                                   anchor=NE,
                                   relief=RIDGE,
                                   width=10
                                   )
        self.err_count_dat_text.set('0')
        self.err_count_dat.grid(row=1,
                                column=6,
                                padx=4,
                                sticky=W
                                )

        # Max tweet queue size
        ## Label
        self.max_tweet_lab = Label(self.info_frame,
                                   text = 'Max Tweet Q size: ',
                                   justify=RIGHT,
                                   anchor=NE,
                                   )
        self.max_tweet_lab.grid(row=2,
                                column=0,
                                sticky=E+W
                                )

        ## Data
        self.max_tweet_dat_text = StringVar()
        self.max_tweet_dat = Label(self.info_frame,
                                   textvariable=self.max_tweet_dat_text,
                                   justify=LEFT,
                                   anchor=NE,
                                   relief=RIDGE,
                                   width=10
                                   )
        self.max_tweet_dat_text.set('0')
        self.max_tweet_dat.grid(row=2,
                                column=1,
                                padx=4,
                                sticky=W
                                )
        
        # Max db queue size
        ## Label
        self.max_db_lab = Label(self.info_frame,
                                text = 'Max DB Q size: ',
                                justify=RIGHT,
                                anchor=NE,
                                )
        self.max_db_lab.grid(row=3,
                             column=0,
                             sticky=E+W
                             )

        ## Data
        self.max_db_dat_text = StringVar()
        self.max_db_dat = Label(self.info_frame,
                                textvariable=self.max_db_dat_text,
                                justify=LEFT,
                                anchor=NE,
                                relief=RIDGE,
                                width=10
                                )
        self.max_db_dat_text.set('0')
        self.max_db_dat.grid(row=3,
                             column=1,
                             padx=4,
                             sticky=W
                             )

        
        # Tweet rate
        ## Label
        self.tweet_rate_lab = Label(self.info_frame,
                                    text = 'Tweet rate: ',
                                    justify=RIGHT,
                                    anchor=NE,
                                    )
        self.tweet_rate_lab.grid(row=2,
                                 column=2,
                                 sticky=E+W
                                 )

        ## Data
        self.tweet_rate_dat_text = StringVar()
        self.tweet_rate_dat = Label(self.info_frame,
                                    textvariable=self.tweet_rate_dat_text,
                                    justify=RIGHT,
                                    anchor=NE,
                                    relief=RIDGE,
                                    width=10
                                    )
        self.tweet_rate_dat_text.set('0')
        self.tweet_rate_dat.grid(row=2,
                                 column=3,
                                 padx=4,
                                 sticky=W
                                 )
        
        # Tweet rate calc
        ## Label
        self.tweet_rate_calc_lab = Label(self.info_frame,
                                    text = 'Tweet rate calc: ',
                                    justify=RIGHT,
                                    anchor=NE,
                                    )
        self.tweet_rate_calc_lab.grid(row=3,
                                 column=2,
                                 sticky=E+W
                                 )

        ## Data
        self.tweet_rate_calc_dat_text = StringVar()
        self.tweet_rate_calc_dat = Label(self.info_frame,
                                    textvariable=self.tweet_rate_calc_dat_text,
                                    justify=RIGHT,
                                    anchor=NE,
                                    relief=RIDGE,
                                    width=10
                                    )
        self.tweet_rate_calc_dat_text.set('0')
        self.tweet_rate_calc_dat.grid(row=3,
                                 column=3,
                                 padx=4,
                                 sticky=W
                                 )

        # DB path
        ## Label
        self.db_path_lab = Label(self.info_frame,
                                 text = 'DB Path: ',
                                 justify=RIGHT,
                                 anchor=NE,
                                 )
        self.db_path_lab.grid(row=4,
                              column=0,
                              sticky=E+W
                              )

        ## Data
        self.db_path_dat_text = StringVar()
        self.db_path_dat = Label(self.info_frame,
                                 textvariable=self.db_path_dat_text,
                                 justify=LEFT,
                                 anchor=NW,
                                 relief=RIDGE,
                                 )
        self.db_path_dat_text.set('0')
        self.db_path_dat.grid(row=4,
                              column=1,
                              columnspan=6,
                              padx=4,
                              sticky=E+W
                              )
        self.db_path_dat_text.set(self.db_path)

        # DB file size
        ## Label
        self.db_file_size_lab = Label(self.info_frame,
                                      text = 'DB File Size: ',
                                      justify=RIGHT,
                                      anchor=NE,
                                      )
        self.db_file_size_lab.grid(row=2,
                                   column=5,
                                   sticky=E+W
                                   )

        ## Data
        self.db_file_size_dat_text = StringVar()
        self.db_file_size_dat = Label(self.info_frame,
                                      textvariable=self.db_file_size_dat_text,
                                      justify=LEFT,
                                      anchor=NE,
                                      relief=RIDGE,
                                      width=10
                                      )
        self.db_file_size_dat_text.set('0')
        self.db_file_size_dat.grid(row=2,
                                   column=6,
                                   padx=4,
                                   sticky=W
                                   )
        self.db_file_size_dat_text.set('%.2f MB' % round(self.db_file_size, 2))
        
        # Next backup time
        ## Label
        self.db_next_backup_timer_lab = Label(self.info_frame,
                                              text='Next backup in: ',
                                              justify=RIGHT,
                                              anchor=NE,
                                              )
        self.db_next_backup_timer_lab.grid(row=3,
                                           column=5,
                                           sticky=E+W
                                           )

        ## Data
        self.db_next_backup_timer_dat_text = StringVar()
        self.db_next_backup_timer_dat = Label(
            self.info_frame,
            textvariable=self.db_next_backup_timer_dat_text,
            justify=LEFT,
            anchor=NE,
            relief=RIDGE,
            width=10
            )
        self.db_next_backup_timer_dat_text.set('0')
        self.db_next_backup_timer_dat.grid(row=3,
                                           column=6,
                                           padx=4,
                                           sticky=W
                                           )
        self.db_next_backup_timer_dat_text.set('00:00:00')
        

        #-------------------------------------------------------------
        # Message Region
        #-------------------------------------------------------------

        self.message_frame = Frame(self.mainframe)
        self.message_frame.pack(fill=BOTH,
                                ipadx=region_padding,
                                ipady=region_padding,
                                expand=1
                                )

        # Allow message box to expand horizontally
        self.message_frame.columnconfigure(0, weight=1)

        # Allow message box to expand vertically
        self.message_frame.rowconfigure(0, weight=1)

        # Messages
        ## Data
        self.message_dat = ScrolledText(master=self.message_frame,
                                        wrap=WORD,
                                        height=10
                                        )
        self.message_dat.insert(INSERT, 'Ready to stream')
        self.message_dat["state"] = DISABLED
        self.message_dat.grid(row=0,
                              padx=5,
                              sticky=E+W+S+N
                              )


        #-------------------------------------------------------------
        # Footer Region
        #-------------------------------------------------------------
           
        self.footer_frame = Frame(self.mainframe)
        self.footer_frame.pack(fill=BOTH,
                               padx=region_padding,
                               pady=region_padding,
                               expand=0
                               )

        # Allow to expand to keep close button to the right
        self.footer_frame.columnconfigure(0, weight=1)
        
        # Close button
        self.close_btn = Button(self.footer_frame, command=self.shutdown)
        self.close_btn.configure(text='Close')
        self.close_btn.grid(row=0,
                            padx=button_padding,
                            pady=button_padding,
                            sticky=E
                            )

        #self.log.info('\n{0}\nGUI Initialized\n{0}\n'.format('*'*70))
        
    def launch(self):
        self.init_db()
        self.log.info('Launching interface') # @DEBUG
        self.root.mainloop()
        self.ql.stop()

    def update(self):
        # get sizes of processing queues
        tweet_queue_size = self.twq.qsize()

        # Get updates from count queues
        while not self.db_count_q.empty():
            self.db_count += self.db_count_q.get_nowait()

        while not self.tweet_count_q.empty():
            self.tweet_count += self.tweet_count_q.get_nowait()

        # Check backup status
        self.check_backup()
        
        # update display variables
        ## Tweet queue size
        ### Append new size
        self.twq_sizes.append(tweet_queue_size)

        ### Adjust size of queue
        while len(self.twq_sizes) > self.q_smoothing:
            self.twq_sizes.pop(0)

        ### get max tweet queue length
        max_twq_size = max(self.twq_sizes)

        ### set display of tweet queue sizes
        self.tq_dat_text.set(str(max_twq_size))

        ## Max tweet queue size
        if int(self.max_tweet_dat_text.get()) < int(tweet_queue_size):
            self.max_tweet_dat_text.set(str(tweet_queue_size))

        ## Tweets received count
        self.tweet_count_dat_text.set(str(self.tweet_count))

        ## DB write count
        self.db_count_dat_text.set(str(self.db_count))

        ## time elapsed
        time_strip = r'\.\d*$'
        time_elapsed = dt.now() - self.start_time
        time_elapsed_str = re.sub(time_strip, '', str(time_elapsed))

        self.time_elapsed_dat_text.set(time_elapsed_str)

        ## Tweet rate
        ### get current time and count
        current_time = dt.now()
        current_count = self.tweet_count
        
        ### get the first record from the queue
        first_count, first_time = self.rates.pop(0)

        ### get time difference in seconds
        tdiff = current_time - first_time
        tdiff = tdiff.total_seconds()

        ### get different in count
        countdiff = current_count - first_count

        ### prevent division by zero
        if tdiff == 0:
            current_rate = 0
        else:
            current_rate = countdiff/tdiff

        ### add new rate to list
        self.rates.append((current_count, current_time))

        ### ensure that rates array is the right length
        while len(self.rates) > self.rate_smoothing:
            self.rates.pop(0)

        ### Update display
        self.tweet_rate_dat_text.set('%.2f' % round(current_rate, 2))
        #sum_rate = '%.1f' % sum(self.rates)
        self.tweet_rate_calc_dat_text.set('{}/{}'.format(
            countdiff, '%.2f' % round(tdiff, 2)))

        ## Errors
        self.err_count_dat_text.set(self.err_count)

        ## DB File size
        ### Update DB file size
        self.db_file_size = (os.stat(self.db_path).st_size/(1024**2)
                             if os.path.isfile(self.db_path)
                             else 0)
        self.db_file_size_dat_text.set('%.2f MB' % self.db_file_size) # Already converted to megabytes

        ## DB Backup Timer
        next_backup_time_str = str(self.next_backup_time - dt.now())
        next_backup_time_str = re.sub(time_strip, '', next_backup_time_str)
        self.db_next_backup_timer_dat_text.set(next_backup_time_str)

        # continue updating if the stream hasn't been stopped
        if not ((not self.streaming)       and
                self.twq.empty()           and
                self.stream_msgq.empty()   and
                self.db_count_q.empty()    and
                self.tweet_count_q.empty() and
                self.db_count_q.empty()):
            self.root.after(200, self.update)


    ##################################################################
    # Stream Management
    ##################################################################

    def start_stream(self):
        # Gather contents of follow and track widgets into self.follow and self.track
        self.xfer_follow()
        self.xfer_track()

        # Ditch empty strings
        if self.follow=='':
            self.follow = None
        if self.track=='':
            self.track = None
        
        # Check that query parameters are provided
        if(self.follow is None and self.track is None):
            msgbox.showerror('Query Error', 'No query parameters provided.\nPlease use the follow and track fields to enter parameters for the streaming query.')
            return 

        # Gather parameters
        params = {}

        if self.follow is not None:
            params['follow'] = self.follow
        if self.track is not None:
            params['track'] = self.track
        params['stall_warnings'] = 'true'

        self.stream_params = params

        # initialize queues
        ## Holds Tweets/messages from Twitter, enqueued by StreamWorkers
        self.twq = multiprocessing.Queue()

        ## message queues
        self.stream_msgq = multiprocessing.Queue()

        ## Holds error messages enqueud by workers for display in message box
        #self.errq = ERRQ

        ## Holds increments from DB workers for each row written
        self.db_count_q = multiprocessing.Queue()

        ## Holds increments from StreamWorkers for each tweet received
        self.tweet_count_q = multiprocessing.Queue()

        # Update db file path

        # Initialize workers
        self.sws = [StreamWorker(self.twq, self.stream_msgq, self.errq, self.tweet_count_q, db_path=self.db_path, chunk_size=self.chunk_size.get(), **self.stream_params)
                    for x in range(int(self.num_sws.get()))]

        self.dbws = [DBWorker(self.twq, self.errq, self.db_count_q, db_path=self.db_path)
                    for x in range(int(self.num_dbws.get()))]

        # Add new workers to list of processes used
        self.procs_used += self.sws + self.dbws
        
        if not self.streaming:
            self.add_message('\nStarting stream...')
            self.streaming = True
            # start subprocesses
            for sw in self.sws:
                sw.start()
                self.add_message('\n   Stream Worker {}-{} started'.format(sw.name, sw.pid))
            for dbw in self.dbws:
                dbw.start()
                self.add_message('\n   DB Worker {}-{} started'.format(dbw.name, dbw.pid))

            self.add_message('\nStreaming...')

            # change streaming button text
            self.stream_btn.configure(text='Stop Streaming')

            # Set start time
            self.start_time = dt.now()
            
            # start updates
            self.update()

    def stop_stream(self):
        """
        Complete streaming tasks and shutdown the stream
        """
        if self.streaming:
            # Add message
            self.add_message('\n\nStopping stream...')

            # shut down workers
            for x in range(0, len(self.sws)):
                self.stream_msgq.put(STOP_MESSAGE)

            # join workers
            for sw in self.sws:
                self.add_message('\n   Stopping Stream Worker {}-{}...'.format(sw.name, sw.pid))
                if sw.is_alive():
                    try:
                        sw.join(timeout=5)
                    except multiprocessing.TimeoutError:
                        sw.terminate()
                        self.add_message('Terminated.')
                    else:
                        self.add_message('Joined.')
                else:
                    self.add_message('Dead.')
                        
            for dbw in self.dbws:
                self.add_message('\n   Stopping DB Worker {}-{}...'.format(dbw.name,dbw.pid))
                if dbw.is_alive():
                    try:
                        dbw.join(timeout=5)
                    except multiprocessing.TimeoutError:
                        dbw.terminate()
                        self.add_message('Terminated.')
                    else:
                        self.add_message('Joined.')
                else:
                    self.add_message('Dead.')

            # added stopped message
            self.add_message('\nStream stopped')

            # change streaming button text
            self.stream_btn.configure(text='Start Streaming')

            # set streaming flag
            self.streaming = False

            # final gui update
            self.update()


    def restart_stream(self, e=None, tb=None):
        """
        """
        if e is not None or tb is not None:
            self.err_message(e=e, tb=tb)
        self.add_message('\nRestarting stream... ')
        self.stop_stream()
        self.start_stream()

    def toggle_stream(self):
        if self.streaming:
            self.stop_stream()
        else:
            self.start_stream()


    ##################################################################
    # DB File Management
    ##################################################################

    def archive_db(self):
        self.add_message('\n\nArchiving DB file...')
        self.log.info('Archiving DB file')
        self.add_message('\n    Setting new DB file')

        # get new db file path
        try:
            self.set_db_file()
        except Exception as e:
            self.log.exception('Error setting new DB file')
            raise
                
        # replace old objects
        ## Queues
        old_twq = self.twq
        old_errq = self.errq
        old_tweet_count_q = self.tweet_count_q
        old_db_count_q = self.db_count_q
        old_stream_msgq = self.stream_msgq

        ## Workers
        old_sws = self.sws
        old_dbws = self.dbws

        # create new queues, workers
        self.add_message('\n    Creating new queues and workers...')
        self.twq = multiprocessing.Queue()
        self.errq = multiprocessing.Queue()
        self.tweet_count_q = multiprocessing.Queue()
        self.db_count_q = multiprocessing.Queue()
        self.stream_msgq = multiprocessing.Queue()
        
        self.dbws = [DBWorker(self.twq, self.errq, self.db_count_q, db_path=self.db_path)
                    for x in range(int(self.num_dbws.get()))]
        self.sws = [StreamWorker(self.twq, self.stream_msgq, self.errq, self.tweet_count_q, db_path=self.db_path, chunk_size=self.chunk_size.get(), **self.stream_params)
                    for x in range(int(self.num_sws.get()))]

        # start new stream, stop old stream
        self.add_message('\n    Starting new streams...')
        self.log.info('Starting new stream')
        for sw in self.sws:
            sw.start()
            self.add_message('\n        Stream Worker {}-{} started...'.format(sw.name, sw.pid))
            self.log.info('Stream Worker {}-{} started'.format(sw.name, sw.pid))

        self.add_message('\n    Stopping stream workers...')
        self.log.info('Stopping stream workers')
        # shut down workers
        for x in range(0, len(old_sws)):
            old_stream_msgq.put(STOP_MESSAGE)

        # init new file
        self.add_message('\n    Initializing DB... ')
        self.init_db()
        self.add_message('\n    DB initialization complete')
        
        # join stream workers
        for sw in old_sws:
            self.add_message('\n   Stopping Stream Worker {}-{}...'.format(sw.name, sw.pid))
            if sw.is_alive():
                try:
                    sw.join(timeout=5)
                except multiprocessing.TimeoutError:
                    sw.terminate()
                    self.add_message('Terminated.')
                else:
                    self.add_message('Joined.')
            else:
                self.add_message('Dead.')

        # start new DB workers
        self.add_message('\n    Starting new DB Workers')
        for dbw in self.dbws:
            dbw.start()
            self.add_message('\n       DB Worker {}-{} started'.format(dbw.name, dbw.pid))

        # churn queues
        self.add_message('\n    Churning queues')
        qcs = []
#        qcs.append(QueueChurner(old_twq, self.twq))
        qcs.append(QueueChurner(old_errq, self.errq))
        qcs.append(QueueChurner(old_tweet_count_q, self.tweet_count_q))
        qcs.append(QueueChurner(old_db_count_q, self.db_count_q))
#        qcs.append(QueueChurner(old_stream_msgq, self.stream_msgq)) # Don't want to send messages intended for old workers to new ones
        self.add_message('\n        Starting Queue Churners')
        for qc in qcs:
            qc.start()
            self.add_message('\n   Started Queue Churner {}-{}...'.format(qc.name, qc.pid))
        self.add_message('\n        Joining Queue Churners')
        for qc in qcs:
            qc.join()
            self.add_message('\n   Joined Queue Churner {}-{}...'.format(qc.name, qc.pid))

        # Join old DB workers
        for dbw in old_dbws:
            self.add_message('\n   Stopping DB Worker {}-{}...'.format(dbw.name,dbw.pid))

            if dbw.is_alive():
                try:
                    dbw.join(timeout=5)
                except multiprocessing.TimeoutError:
                    dbw.terminate()
                    self.add_message('Terminated.')
                else:
                    self.add_message('Joined.')
            else:
                self.add_message('Dead.')

        # Add new dbws to list of processes used
        self.procs_used += self.dbws + self.sws
        
        # Update display
        self.db_path_dat_text.set(self.db_path)

        self.add_message('\n** DB archiving complete **\n')
    
    def set_db_file(self, path=None):
        # Set db path to value provided in call, if provided
        if path is not None:
            self.db_path = os.path.join(DB_DIR, path)
        # No value provided in call -- set new file
        else:
            self.db_path = os.path.join(DB_DIR, self.get_new_db_filename())
        self.db_file_size = 0

    def get_new_db_filename(self):
        fname = dt.now().strftime('{}_%Y-%m-%d_%H-%M-%S{}').format(DB_BASE_FILENAME, DB_SUFFIX)
        return fname

    def load_current_db_file(self):
        # get listing from db directory
        db_files = os.listdir(DB_DIR)
        
        # Filter file names -- old code; filtering no longer necessary
        fn_pattern = DB_FILENAME_PATTERN.format('.*')
        fn_pattern = re.compile(fn_pattern+'$')
        db_files = [x for x in db_files if fn_pattern.search(x) is not None]

        # Sort descending so that first file is the most recent (greatest time)
        db_files.sort(reverse=True)

        path = None

        if len(db_files) >= 1:
            # at least one matching file
            path = db_files[0]
        self.set_db_file(path=path)
        
    def check_backup(self):
        # update db_file_size
        self.db_file_size = os.stat(self.db_path).st_size/(1024**2)
        # Check whether next backup time has arrived or
        # DB file size exceeds limit
        if (self.next_backup_time <= dt.now() or
            self.db_file_size >= self.db_file_size_limit):
            # do backup 
            self.archive_db()
            # reset timer
            self.next_backup_time = dt.now() + self.backup_interval            

    def init_db(self):
        self.add_message('\nInitializing Database...')
        try:
            self.setup_db()
        except Exception as e:
            self.add_message('\nError initializing database:\n\n')
            self.err_message(e)
        else:
            self.add_message(' DONE.')

    def setup_db(self):
        ## Lookup null account ids
        nulls = []
        self.add_message('\n\t\tGathering null account ids...')
        for league in ACCOUNTS.keys():
            for team in ACCOUNTS[league].keys():
                for sn in ACCOUNTS[league][team].keys():
                    if ACCOUNTS[league][team][sn].get('id', None) is None:
                        nulls.append(screen_name)
        self.add_message(' Done.')

        self.add_message('\n\t\tLooking up ids...')
        null_accts = screen_name_lookup(nulls) if len(nulls) > 0 else []
        null_ids = {x['screen_name'].lower():x['id_str'] for x in null_accts}
        self.add_message(' Done.')

        session = get_session(self.db_path)
    	
    	# Add teams/accounts
        self.add_message('\n\t\tAdding ids to DB...')
        for league_name, teams in ACCOUNTS.items():
    	    for team_name, accts in teams.items():
    	        # add team
    	        t = Team(name=team_name, league=league_name)
    	        t = session.merge(t)
    	        try:
    	            session.commit()
    	        except:
    	            session.rollback()
    	            raise
    	
    	        for sn, acc in accts.items():
    	            # get account id
    	            acc_id = null_ids.get(sn, acc.get('id', None))
    	
    	            # create account with id and merge with DB
    	            a = Account(id_str=acc_id)
    	            a = session.merge(a)
    	            a.team = t
    	            if acc.get('description', None) is not None:
    	                a.description = acc.get('description')
    	            if acc.get('type', None) is not None:
    	                a.acct_type = acc.get('type')
    	            
    	
    	            # add user, if it doesn't exist
    	            if a.user is None:
    	                a.user = User(id_str = acc_id)
    	
    	            a.user.screen_name = sn
    	            try:
    	                session.commit()
    	            except:
    	                session.rollback()
    	                raise
    	
        session.close()
        self.add_message(' Done.')


    


    ##################################################################
    # Closing/quitting/shutting down
    ##################################################################

    def shutdown(self):
        """
        Shutdown the program.
        """
        self.stop_stream()
        self.root.destroy()
        # @TO-DO: cleanup multiprocessing objects
        while len(self.procs_used) > 0:
            procs_start = len(self.procs_used)
            for proc in self.procs_used:
                proc.join()
            self.procs_used = [proc for proc in self.procs_used if proc.is_alive()]
            procs_end = len(self.procs_used)
            self.log.info('Joining procs_used: {} procs entered loop, {} procs leaving'.format(procs_start, procs_end))
        self.log.info('Shutown complete')
        
    def window_close(self):
        """
        Handle closing of window
        """
        if msgbox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.shutdown()

    ##################################################################
    # Display Management
    ##################################################################

    #____Message display______________________________________________

    def add_message(self, msg):
        self.message_dat["state"] = NORMAL
        self.message_dat.insert(END, '{}'.format(msg))
        self.message_dat["state"] = DISABLED
        self.message_dat.yview(END)
        self.root.update_idletasks()

    def err_message(self, e=None, tb=None):
        print('*'*70, '\nGetting Error Message...') # @DEBUG
        err = tb
        if tb is None:
            print('    No traceback. Getting traceback') # @DEBUG
            err = traceback.format_exc()
        print('    adding error message to gui') # @DEBUG
        self.add_message('\n\n'+err)
        print('    added error message to gui') # @DEBUG

    
    #____Follow/Track Settings________________________________________

    def load_follow(self):
        # collect labels from checkbuttons
        # for each checked box, get accounts from db
        clusters = [(val[0],val[1]) for key, val in self.follow_selectors.items() if val[2]]

        # get session
        session = get_session(self.db_path)

        # query for accounts in clusters
        ## get (legue, account type, id) tuples for all Accounts
        res = session.query(Team.league, Account.acct_type, Account.id_str).join(Account,Team)
        
        ## filter result by clusters
        accts = [x[2] for x in res.all() if (x[0], x[1]) in clusters]

        self.clear_follow()

        acct_string = ','.join(accts)
        self.follow_dat.insert(INSERT, acct_string)

    def xfer_follow(self):
        s = self.follow_dat.get(1.0, END)
        # strip whitespace
        s = re.sub(r'\s', '', s)

        self.follow = None if s=='' else s

    def xfer_track(self):
        s = self.track_dat.get(1.0, END)
        # strip whitespace
        s = re.sub(r'\s', '', s)

        self.track = None if s=='' else s

    def set_follow_selector(self, grp, dat):
        """
        handler for follow checkbuttons
        @param dat: a tuple of (group, type, boolean flag)
        """
        self.follow_selectors[grp]=dat

    def clear_follow(self):
        self.follow_dat.delete(1.0, END)

    def get_follow(self):
        pass

    def load_track(self):
        pass

    def clear_track(self):
        pass

    def get_track(self):
        pass

if __name__ == '__main__':
    fg = FanGUI()
    fg.launch()

