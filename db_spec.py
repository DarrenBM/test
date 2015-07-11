# @TO-DO: Create views (see fantwitter)


from sqlalchemy import (Column, String, Integer, Float, DateTime,
                        Boolean, ForeignKey, Index, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
#from fanworkers_new import *

Base = declarative_base()

# Accounts for generating queries
class Account(Base):
    __tablename__ = 'accounts'

#    id          = Column(Integer, primary_key=True)
    id_str      = Column(String, ForeignKey('users.id_str'), primary_key=True)
    team_name   = Column(String, ForeignKey('teams.name'))
    acct_type   = Column(String) # could be enum
    description = Column(String)

    user = relationship('User')
    
# Teams and leagues
class Team(Base):
    __tablename__ = 'teams'

    name   = Column(String, primary_key=True)
    league = Column(String)
    
    accounts = relationship('Account', backref='team')

# Users, including those pulled from tweet data, as well as followed
# accounts
class User(Base):
    __tablename__ = 'users'

    id_str      = Column(String, primary_key = True)
    #screen_name = Column(String, index=True, unique=True)
    # @TO-DO: move screen_name to userprops
    
    props  = relationship('UserProps', backref='user')


# Data about users, timestamped, to capture changes in, e.g., number of statuses
class UserProps(Base): # Need to add a timestamp to these
    __tablename__ = 'userprops'

    id                    = Column(Integer, primary_key=True)
    user_id_str           = Column(String, ForeignKey('users.id_str'))
    screen_name           = Column(String)
    captured_at           = Column(DateTime)
    created_at            = Column(DateTime)
    listed_count          = Column(Integer)
    statuses_count        = Column(Integer)
    favourites_count      = Column(Integer)
    followers_count       = Column(Integer)
    verified              = Column(Boolean)
    default_profile_image = Column(Boolean)
    geo_enabled           = Column(Boolean)
    friends_count         = Column(Integer)
    
# Main tweet data
class Tweet(Base):
    __tablename__ = 'tweets'

    id_str                    = Column(String, primary_key=True)
    created_at                = Column(DateTime)
    captured_at               = Column(DateTime)
    stream_session_id         = Column(Integer, ForeignKey('streamsessions.id'))
    user_id_str               = Column(String, ForeignKey('users.id_str'))
    in_reply_to_status_id_str = Column(String, ForeignKey('tweets.id_str')) # new table -- This is not circular, it's allowed. should recursively pull replies until (a) original is in DB or (b) there are no more
    rt_id_str                 = Column(String, ForeignKey('tweets.id_str'))
    tb_char_count             = Column(Integer)
    char_count                = Column(Integer)
    tb_char_count             = Column(Integer)
    sentence_count            = Column(Integer)
    word_count                = Column(Integer)
    sent_polarity             = Column(Float)
    sent_subjectivity         = Column(Float)
    deleted                   = Column(Boolean, default=False)

    user = relationship('User',
                        backref='tweets',
                        foreign_keys=[user_id_str])
    replies = relationship('Tweet',
                           backref=backref('in_reply_to',
                                           remote_side=[id_str]),
                           foreign_keys=[in_reply_to_status_id_str])
    retweets = relationship('Tweet',
                            backref=backref('original',
                                            remote_side=[id_str]),
                            foreign_keys=[rt_id_str])
    stream_session = relationship('StreamSession',
                           backref='tweets')

    
class SentimentCheck(Base):
    __tablename__ = 'sentimentcheck'

    tweet_id    = Column(String,
                         ForeignKey('tweets.id_str'),
                         primary_key=True)
    tweet_text  = Column(String)

class Mention(Base):
    __tablename__ = 'mentions'

    user_id  = Column(String,
                      ForeignKey('users.id_str'),
                      primary_key=True)
    tweet_id = Column(String,
                      ForeignKey('tweets.id_str'),
                      primary_key=True)

    mentioned_user   = relationship('User', backref='mentions')
    mentioning_tweet = relationship('Tweet', backref='mentions')

class StreamSession(Base):
    __tablename__ = 'streamsessions'

    id        = Column(Integer, primary_key=True)
    starttime = Column(DateTime)
    endtime   = Column(DateTime)
    limit     = Column(Integer, default=0) # @TO-DO: break these out into a new table with an entry for each message, timestamps

## class Game(Base):
##     __tablename__ = 'games'

##     # Have to use an id--can't use composite key of, e.g., starttime +
##     # team name--because some teams can play multiple games on the
##     # same day, and start time data might be limited for some games.
##     # -- Can use game number + season + team
##     ## ADD WIN % -- NEED FORMULA ##

##     #abbreviation = Column(String)
##     assists = Column(Integer)
##     at_bats = Column(Integer)
##     ats_margin = Column(Float)
##     ats_streak = Column(Integer)
##     attendance = Column(Integer)
##     #average_net_punt_yards = Column(Float)
##     #average_punt_yards = Column(Float)
##     biggest_lead = Column(Integer)
##     #blocked_extra_points = Column(Integer)
##     #blocked_field_goals = Column(Integer)
##     #blocked_punts = Column(Integer)
##     #blocks = Column(Integer)
##     c = Column(Boolean)
##     #city = Column(String)
##     close_line = Column(Float)
##     close_total = Column(Float)
##     completions = Column(Integer)
##     conference = Column(String)
## #    date = 
##     day = Column(String)
##     defensive_rebounds = Column(Integer)
##     o_defensive_rebounds = Column(Integer)
##     div = Column(Boolean)
##     division = Column(String)
##     double_header = Column(Integer)
##     double_plays = Column(Integer)
##     dpa = Column(Float)
##     dps = Column(Float)
##     drives = Column(Integer)
##     earned_runs = Column(Integer)
##     errors = Column(Integer)
##     o_errors = Column(Integer)
##     f = Column(Boolean)
##     faceoffs_won = Column(Integer)
##     fast_break_points = Column(Integer)
##     field_goals = Column(Integer)
##     field_goals_attempted = Column(Integer)
##     first_downs = Column(Integer)
##     free_throws_attempted = Column(Integer)
##     free_throws_made = Column(Integer)
##     fourth_downs_attempted = Column(Integer)
##     fourth_downs_made = Column(Integer)
##     fumble_return_touchdowns = Column(Integer)
##     #fumbles = Column(Integer)
##     #o_fumbles = Column(Integer)
##     fumbles_lost = Column(Integer)
##     #full_name = Column(String)
##     game_number = Column(Integer)
##     goal_to_go_attempted = Column(Integer)
##     goal_to_go_made = Column(Integer)
##     hits = Column(Integer)
##     hr = Column(Integer)
##     #il = Column(Integer)
##     innings_led = Column(Integer)
##     innings_tied = Column(Integer)
##     #it = Column(Integer)
##     interception_return_yards = Column(Float)
##     interception_returns = Column(Integer)
##     interception_touchdowns = Column(Integer)
##     interceptions = Column(Integer)
##     kicking_extra_points = Column(Integer)
##     kicking_extra_points_attempted = Column(Integer)
##     kickoff_return_touchdowns = Column(Integer)
##     kickoff_return_yards = Column(Float)
##     kickoff_returns = Column(Integer)
##     kickoffs = Column(Integer)
##     kickoffs_for_touchback = Column(Integer)
##     kickoffs_in_end_zone = Column(Integer)
##     lead_changes = Column(Integer)
##     left_on_base = Column(Integer)
##     line = Column(Float)
##     #location = Column(String)
##     losses = Column(Integer)
##     margin = Column(Integer)
##     m1 = Column(Integer)
##     m2 = Column(Integer)
##     m3 = Column(Integer)
##     m4 = Column(Integer)
##     m5 = Column(Integer)
##     m6 = Column(Integer)
##     m7 = Column(Integer)
##     m8 = Column(Integer)
##     m9 = Column(Integer)
##     m10 = Column(Integer)
##     matchup_losses = Column(Integer)
##     matchup_wins = Column(Integer)
##     minutes = Column(Float)
##     #month = Column(String)
##     ngt = Column(Boolean)
##     offensive_rebounds = Column(Integer)
##     open_line = Column(Float)
##     open_total = Column(Float)
##     #opponents = Column(String)
##     ou_margin = Column(Float)
##     ou_streak = Column(Integer)
##     over = Column(Float)
##     overtime = Column(Boolean)
##     p1 = Column(Integer)
##     p2 = Column(Integer)
##     p3 = Column(Integer)
##     p4 = Column(Integer)
##     p5 = Column(Integer)
##     p6 = Column(Integer)
##     p7 = Column(Integer)
##     p8 = Column(Integer)
##     p9 = Column(Integer)
##     p10 = Column(Integer)
##     passes = Column(Integer)
##     passing_first_downs = Column(Integer)
##     passing_touchdowns = Column(Integer)
##     passing_yards = Column(Float)
##     penalties = Column(Integer)
##     penalty_first_downs = Column(Integer)
##     penalty_minutes = Column(Integer)
##     penalty_yards = Column(Float)
##     pitchers_used = Column(String)
##     percent_bets = Column(Float)
##     percent_over_bets = Column(Float)
##     percent_under_bets = Column(Float)
##     period_scores = Column(String)
##     playoffs = Column(Boolean)
##     plays = Column(Integer)
##     points = Column(Integer)
##     points_in_the_paint = Column(Integer)
##     punt_return_touchdowns = Column(Integer)
##     punt_return_yards = Column(Float)
##     punt_returns = Column(Integer)
##     punts = Column(Integer)
##     rebounds = Column(Integer)
##     red_zones_attempted = Column(Integer)
##     red_zones_made = Column(Integer)
##     rest = Column(Integer)
##     return_yards = Column(Float)
##     round = Column(Integer)
##     run_line = Column(Float)
##     run_line_runs = Column(Float)
##     run_line_streak = Column(Integer)
##     rushes = Column(Integer)
##     rushes_for_a_loss = Column(Integer)
##     rushing_first_downs = Column(Integer)
##     rushing_touchdowns = Column(Integer)
##     rushing_yards = Column(Float)
##     rushing_yards_lost = Column(Float)
##     s1 = Column(Integer)
##     s2 = Column(Integer)
##     s3 = Column(Integer)
##     s4 = Column(Integer)
##     s5 = Column(Integer)
##     s6 = Column(Integer)
##     s7 = Column(Integer)
##     s8 = Column(Integer)
##     s9 = Column(Integer)
##     s10 = Column(Integer)
##     sack_yards = Column(Float)
##     sacks = Column(Integer)
##     safeties = Column(Integer)
##     scored_first = Column(Boolean)
##     season = Column(Integer)
##     seed = Column(Integer)
##     series_game = Column(Integer)
##     series_games = Column(Integer)
##     series_losses = Column(Integer)
##     series_wins = Column(Integer)
##     shots_on_goal = Column(Integer)
##     site = Column(String)
##     site_streak = Column(Integer)
##     snf = Column(Boolean)
##     start_time = Column(Integer)
##     #starter = Column(String)
##     starter_losses = Column(Integer)
##     starter_matchup_losses = Column(Integer)
##     starter_matchup_wins = Column(Integer)
##     starter_rest = Column(Integer)
##     starter_throws = Column(Integer)
##     starter_wins = Column(Integer)
##     steals = Column(Integer)
##     streak = Column(Integer)
##     strike_outs = Column(Integer)
##     #surface = Column(String)
##     team = Column(String, ForeignKey('teams.name'))
##     team_left_on_base = Column(Integer)
##     team_rebounds = Column(Integer)
##     #temperature = Column(Float)
##     third_downs_attempted = Column(Integer)
##     third_downs_made = Column(Integer)
##     three_pointers_attempted = Column(Integer)
##     three_pointers_made = Column(Integer)
##     time_of_game = Column(Integer)
##     time_of_possession = Column(Float)
##     time_zone = Column(String)
##     times_tied = Column(Integer)
##     total = Column(Integer)
##     touchdowns = Column(Integer)
##     turnover_margin = Column(Integer)
##     turnovers = Column(Integer)
##     two_point_conversions = Column(Integer)
##     two_point_conversions_attempted = Column(Integer)
##     under = Column(Float)
##     walks = Column(Integer)
##     week = Column(Integer)
##     wins = Column(Integer)
##     #wp = Column(Float)
    

def get_session(path=None):
    if path is None:
        engine = create_engine('sqlite:///' + DB_PATH, echo=False)
    else:
        engine = create_engine('sqlite:///' + path, echo=False)

    # Create everything
    Base.metadata.create_all(engine)

    # create Session class
    Session = sessionmaker(bind=engine)

    return Session()
        
    
if __name__ == '__main__':
    from sqlalchemy import create_engine
    from datetime import datetime as dt
    from fansettings import *

    ## Lookup null account ids
    nulls = []
    for league in ACCOUNTS.keys():
        for team in ACCOUNTS[league].keys():
            for sn in ACCOUNTS[league][team].keys():
                if ACCOUNTS[league][team][sn].get('id', None) is None:
                    nulls.append(screen_name)
    
    null_accts = screen_name_lookup(nulls) if len(nulls) > 0 else []
    null_ids = {x['screen_name'].lower():x['id_str'] for x in null_accts}

    
    start_time = dt.now()
#    ACCOUNTS['nfl']['nfl_broncos']['milehighreport']['type'] = 'awesome_test' # @DEBUG

    session = get_session('db//testdb_2015-02-11_20-52-42.sqlite_test')

    # Add teams/accounts
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

    print(dt.now()-start_time)
    
