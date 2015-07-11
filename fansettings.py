import re
import os

# Default values/settings

#_____DB File settings________________________________________________
DB_PATH = 'db/testdb.sqlite'
DB_DIR = os.path.dirname(DB_PATH) # dirname extracted from DB_PATH
DB_FILENAME = os.path.basename(DB_PATH) # filename extracted from DB_PATH
DB_BASE_FILENAME = re.sub(r'\.\w*$', '',  DB_FILENAME) # filename with suffix removed
DB_ARCHIVE_DIR = os.path.join(DB_DIR, 'archive')
DB_FILENAME_PATTERN = 'testdb_{}.sqlite'

DB_FN_PATTERN = 'fan_tweets_{}'
DB_SUFFIX = '.sqlite'
DB_FULL_FN_PATTERN = DB_FN_PATTERN + DB_SUFFIX
DB_DIR_NEW = '../data_db'
DB_PATH_PATTERN = os.path.join(DB_DIR_NEW, DB_FULL_FN_PATTERN)

#____Backup settings__________________________________________________
DB_BACKUP_INTERVAL = 24 # Timer in hours
DB_FILE_SIZE_LIMIT = 100 # Limit for size of DB file in megabytes

#____Logging__________________________________________________________
LOG_PATH = 'logs/fan_log_file_ai'
LOG_DIR = os.path.dirname(LOG_PATH)
LOG_FILENAME = os.path.basename(LOG_PATH)
LOG_FORMAT = '%(asctime)s: [%(name)s] %(module)20s.%(funcName)-20s#%(lineno)-5d|%(processName)-20s|%(process)d|%(levelname)s -- %(message)s'

#____Messages_________________________________________________________
START_MESSAGE = '<START_PROCESS>'
STOP_MESSAGE = '<STOP_PROCESS>'
TWEET_MESSAGE = '<TWEET_MESSAGE>'
STOP_STREAM_MESSAGE = '<STOP_STREAM>'
PAUSE_MESSAGE = '<PAUSE_PROCESS>' # unused
RESUME_MESSAGE = '<RESUME_PROCESS>' # unused

#____Accounts to stream_______________________________________________
ACCOUNTS = {
     "mlb": {
          "mlb_angels": {
               "angels": {
                    "description": "Los Angeles Angels official team account",
                    "id": "39392910",
                    "type": "official"
               },
               "halosheaven": {
                    "description": "Account of SBNation blog for Los Angeles Angels fans",
                    "id": "21202783",
                    "type": "blog"
               }
          },
          "mlb_astros": {
               "astros": {
                    "description": "Houston Astros official team account",
                    "id": "52803520",
                    "type": "official"
               },
               "crawfishboxes": {
                    "description": "Account of SBNation blog for Houston Astros fans",
                    "id": "17831093",
                    "type": "blog"
               }
          },
          "mlb_athletics": {
               "athletics": {
                    "description": "Oakland Athletics official team account",
                    "id": "19607400",
                    "type": "official"
               },
               "athleticsnation": {
                    "description": "Account of SBNation blog for Oakland Athletics fans",
                    "id": "47515008",
                    "type": "blog"
               }
          },
          "mlb_bluejays": {
               "bluebirdbanter": {
                    "description": "Account of SBNation blog for Toronto Blue Jays fans",
                    "id": "28002645",
                    "type": "blog"
               },
               "bluejays": {
                    "description": "Toronto Blue Jays official team account",
                    "id": "41468683",
                    "type": "official"
               }
          },
          "mlb_braves": {
               "braves": {
                    "description": "Atlanta Braves official team account",
                    "id": "21436663",
                    "type": "official"
               },
               "talkingchop": {
                    "description": "Account of SBNation blog for Atlanta Braves fans",
                    "id": "1012067395",
                    "type": "blog"
               }
          },
          "mlb_brewers": {
               "brewcrewball": {
                    "description": "Account of SBNation blog for Milwaukee Brewers fans",
                    "id": "21107281",
                    "type": "blog"
               },
               "brewers": {
                    "description": "Milwaukee Brewers official team account",
                    "id": "52824038",
                    "type": "official"
               }
          },
          "mlb_cardinals": {
               "cardinals": {
                    "description": "St. Louis Cardinals official team account",
                    "id": "52847728",
                    "type": "official"
               },
               "vivaelbirdos": {
                    "description": "Account of SBNation blog for St. Louis Cardinals fans",
                    "id": "92352691",
                    "type": "blog"
               }
          },
          "mlb_cubs": {
               "bleedcubbieblue": {
                    "description": "Account of SBNation blog for Chicago Cubs fans",
                    "id": "17845694",
                    "type": "blog"
               },
               "cubs": {
                    "description": "Chicago Cubs official team account",
                    "id": "41144996",
                    "type": "official"
               }
          },
          "mlb_diamondbacks": {
               "azsnakepit": {
                    "description": "Account of SBNation blog for Arizona Diamondbacks fans",
                    "id": "28040711",
                    "type": "blog"
               },
               "dbacks": {
                    "description": "Arizona Diamondbacks official team account",
                    "id": "31164229",
                    "type": "official"
               }
          },
          "mlb_dodgers": {
               "dodgers": {
                    "description": "Los Angeles Dodgers official team account",
                    "id": "23043294",
                    "type": "official"
               },
               "truebluela": {
                    "description": "Account of SBNation blog for Los Angeles Dodgers fans",
                    "id": "24346793",
                    "type": "blog"
               }
          },
          "mlb_giants": {
               "mccoveychron": {
                    "description": "Account of SBNation blog for San Francisco Giants fans",
                    "id": "22037861",
                    "type": "blog"
               },
               "sfgiants": {
                    "description": "San Francisco Giants official team account",
                    "id": "43024351",
                    "type": "official"
               }
          },
          "mlb_indians": {
               "indians": {
                    "description": "Cleveland Indians official team account",
                    "id": "52861612",
                    "type": "official"
               },
               "letsgotribe": {
                    "description": "Account of SBNation blog for Cleveland Indians fans",
                    "id": "23559851",
                    "type": "blog"
               }
          },
          "mlb_mariners": {
               "lookoutlanding": {
                    "description": "Account of SBNation blog for Seattle Mariners fans",
                    "id": "21941423",
                    "type": "blog"
               },
               "mariners": {
                    "description": "Seattle Mariners official team account",
                    "id": "41488578",
                    "type": "official"
               }
          },
          "mlb_marlins": {
               "fishstripes": {
                    "description": "Account of SBNation blog for Miami Marlins fans",
                    "id": "18252117",
                    "type": "blog"
               },
               "marlins": {
                    "description": "Miami Marlins official team account",
                    "id": "52863923",
                    "type": "official"
               }
          },
          "mlb_mets": {
               "amazinavenue": {
                    "description": "Account of SBNation blog for New York Mets fans",
                    "id": "15503429",
                    "type": "blog"
               },
               "mets": {
                    "description": "New York Mets official team account",
                    "id": "39367703",
                    "type": "official"
               }
          },
          "mlb_nationals": {
               "federalbaseball": {
                    "description": "Account of SBNation blog for Washington Nationals fans",
                    "id": "17947488",
                    "type": "blog"
               },
               "nationals": {
                    "description": "Washington Nationals official team account",
                    "id": "39419180",
                    "type": "official"
               }
          },
          "mlb_orioles": {
               "camdenchat": {
                    "description": "Account of SBNation blog for Baltimore Orioles fans",
                    "id": "82256022",
                    "type": "blog"
               },
               "orioles": {
                    "description": "Baltimore Orioles official team account",
                    "id": "39389304",
                    "type": "official"
               }
          },
          "mlb_padres": {
               "gaslampball": {
                    "description": "Account of SBNation blog for San Diego Padres fans",
                    "id": "6998452",
                    "type": "blog"
               },
               "padres": {
                    "description": "San Diego Padres official team account",
                    "id": "37837907",
                    "type": "official"
               }
          },
          "mlb_phillies": {
               "phillies": {
                    "description": "Philadelphia Phillies official team account",
                    "id": "53178109",
                    "type": "official"
               },
               "thegoodphight": {
                    "description": "Account of SBNation blog for Philadelphia Phillies fans",
                    "id": "17827295",
                    "type": "blog"
               }
          },
          "mlb_pirates": {
               "bucsdugout": {
                    "description": "Account of SBNation blog for Pittsburgh Pirates fans",
                    "id": "46425950",
                    "type": "blog"
               },
               "pirates": {
                    "description": "Pittsburgh Pirates official team account",
                    "id": "37947138",
                    "type": "official"
               }
          },
          "mlb_rangers": {
               "lonestarball": {
                    "description": "Account of SBNation blog for Texas Rangers fans",
                    "id": "84443799",
                    "type": "blog"
               },
               "rangers": {
                    "description": "Texas Rangers official team account",
                    "id": "40931019",
                    "type": "official"
               }
          },
          "mlb_rays": {
               "draysbay": {
                    "description": "Account of SBNation blog for Tampa Bay Rays fans",
                    "id": "20635455",
                    "type": "blog"
               },
               "raysbaseball": {
                    "description": "Tampa Bay Rays official team account",
                    "id": "39682297",
                    "type": "official"
               }
          },
          "mlb_reds": {
               "redreporter": {
                    "description": "Account of SBNation blog for Cincinnati Reds fans",
                    "id": "21194766",
                    "type": "blog"
               },
               "reds": {
                    "description": "Cincinnati Reds official team account",
                    "id": "35006336",
                    "type": "official"
               }
          },
          "mlb_redsox": {
               "overthemonster": {
                    "description": "Account of SBNation blog for Boton Red Sox fans",
                    "id": "21119272",
                    "type": "blog"
               },
               "redsox": {
                    "description": "Boton Red Sox official team account",
                    "id": "40918816",
                    "type": "official"
               }
          },
          "mlb_rockies": {
               "purplerow": {
                    "description": "Account of SBNation blog for Colorado Rockies fans",
                    "id": "17827133",
                    "type": "blog"
               },
               "rockies": {
                    "description": "Colorado Rockies official team account",
                    "id": "159143990",
                    "type": "official"
               }
          },
          "mlb_royals": {
               "royals": {
                    "description": "Kansas City Royals official team account",
                    "id": "28603812",
                    "type": "official"
               },
               "royalsreview": {
                    "description": "Account of SBNation blog for Kansas City Royals fans",
                    "id": "27315969",
                    "type": "blog"
               }
          },
          "mlb_tigers": {
               "blessyouboys": {
                    "description": "Account of SBNation blog for Detroit Tigers fans",
                    "id": "15246745",
                    "type": "blog"
               },
               "tigers": {
                    "description": "Detroit Tigers official team account",
                    "id": "30008146",
                    "type": "official"
               }
          },
          "mlb_twins": {
               "twinkietown": {
                    "description": "Account of SBNation blog for Minnesoty Twins fans",
                    "id": "17962664",
                    "type": "blog"
               },
               "twins": {
                    "description": "Minnesoty Twins official team account",
                    "id": "39397148",
                    "type": "official"
               }
          },
          "mlb_whitesox": {
               "southsidesox": {
                    "description": "Account of SBNation blog for Chicago White Sox fans",
                    "id": "356307789",
                    "type": "blog"
               },
               "whitesox": {
                    "description": "Chicago White Sox official team account",
                    "id": "53197137",
                    "type": "official"
               }
          },
          "mlb_yankees": {
               "pinstripealley": {
                    "description": "Account of SBNation blog for New York Yankees fans",
                    "id": "44175777",
                    "type": "blog"
               },
               "yankees": {
                    "description": "New York Yankees official team account",
                    "id": "40927173",
                    "type": "official"
               }
          }
     },
     "nba": {
          "nba_76ers": {
               "liberty_ballers": {
                    "description": "Account of SBNation blog for Philadelphia 76ers fans",
                    "id": "323995477",
                    "type": "blog"
               },
               "sixers": {
                    "description": "Philadelphia 76ers official team account",
                    "id": "16201775",
                    "type": "official"
               }
          },
          "nba_bucks": {
               "brewhoop": {
                    "description": "Account of SBNation blog for Milwaukee Bucks fans",
                    "id": "17907846",
                    "type": "blog"
               },
               "bucks": {
                    "description": "Milwaukee Bucks official team account",
                    "id": "15900167",
                    "type": "official"
               }
          },
          "nba_bulls": {
               "bullsblogger": {
                    "description": "Account of SBNation blog for Chicago Bulls fans",
                    "id": "84952952",
                    "type": "blog"
               },
               "chicagobulls": {
                    "description": "Chicago Bulls official team account",
                    "id": "16212685",
                    "type": "official"
               }
          },
          "nba_cavaliers": {
               "cavs": {
                    "description": "Cleveland Cavaliers official team account",
                    "id": "19263978",
                    "type": "official"
               },
               "fearthesword": {
                    "description": "Account of SBNation blog for Cleveland Cavaliers fans",
                    "id": "363198712",
                    "type": "blog"
               }
          },
          "nba_celtics": {
               "celtics": {
                    "description": "Boston Celtics official team account",
                    "id": "18139461",
                    "type": "official"
               },
               "celticsblog": {
                    "description": "Account of SBNation blog for Boston Celtics fans",
                    "id": "14331674",
                    "type": "blog"
               }
          },
          "nba_clippers": {
               "clippersteve": {
                    "description": "Account of SBNation blog for Los Angeles Clippers fans",
                    "id": "18301465",
                    "type": "blog"
               },
               "laclippers": {
                    "description": "Los Angeles Clippers official team account",
                    "id": "19564719",
                    "type": "official"
               }
          },
          "nba_grizzlies": {
               "memgrizz": {
                    "description": "Memphis Grizzlies official team account",
                    "id": "7117962",
                    "type": "official"
               },
               "sbngrizzlies": {
                    "description": "Account of SBNation blog for Memphis Grizzlies fans",
                    "id": "256593427",
                    "type": "blog"
               }
          },
          "nba_hawks": {
               "atlhawks": {
                    "description": "Atlanta Hawks official team account",
                    "id": "17292143",
                    "type": "official"
               },
               "peachtreehoops": {
                    "description": "Account of SBNation blog for Atlanta Hawks fans",
                    "id": "21119849",
                    "type": "blog"
               }
          },
          "nba_heat": {
               "hothothoops": {
                    "description": "Account of SBNation blog for Miami Heat fans",
                    "id": "45509849",
                    "type": "blog"
               },
               "miamiheat": {
                    "description": "Miami Heat official team account",
                    "id": "11026952",
                    "type": "official"
               }
          },
          "nba_hornets": {
               "at_the_hive": {
                    "description": "Account of SBNation blog for Charlotte Hornets fans",
                    "id": "304202238",
                    "type": "blog"
               },
               "hornets": {
                    "description": "Charlotte Hornets official team account",
                    "id": "21308488",
                    "type": "official"
               }
          },
          "nba_jazz": {
               "slcdunk": {
                    "description": "Account of SBNation blog for Utah Jazz fans",
                    "id": "20294102",
                    "type": "blog"
               },
               "utahjazz": {
                    "description": "Utah Jazz official team account",
                    "id": "18360370",
                    "type": "official"
               }
          },
          "nba_kings": {
               "sacramentokings": {
                    "description": "Sacramento Kings official team account",
                    "id": "667563",
                    "type": "official"
               },
               "sactownroyalty": {
                    "description": "Account of SBNation blog for Sacramento Kings fans",
                    "id": "19654452",
                    "type": "blog"
               }
          },
          "nba_knicks": {
               "nyknicks": {
                    "description": "New York Knicks official team account",
                    "id": "20265254",
                    "type": "official"
               },
               "ptknicksblog": {
                    "description": "Account of SBNation blog for New York Knicks fans",
                    "id": "836076426",
                    "type": "blog"
               }
          },
          "nba_lakers": {
               "lakers": {
                    "description": "Los Angeles Lakers official team account",
                    "id": "20346956",
                    "type": "official"
               },
               "lakersblog_ssr": {
                    "description": "Account of SBNation blog for Los Angeles Lakers fans",
                    "id": "2531330178",
                    "type": "blog"
               }
          },
          "nba_magic": {
               "oppmagicblog": {
                    "description": "Account of SBNation blog for Orlando Magic fans",
                    "id": "114911845",
                    "type": "blog"
               },
               "orlandomagic": {
                    "description": "Orlando Magic official team account",
                    "id": "19537303",
                    "type": "official"
               }
          },
          "nba_mavericks": {
               "dallasmavs": {
                    "description": "Dallas Mavericks official team account",
                    "id": "22185437",
                    "type": "official"
               },
               "mavsmoneyball": {
                    "description": "Account of SBNation blog for Dallas Mavericks fans",
                    "id": "85135948",
                    "type": "blog"
               }
          },
          "nba_nets": {
               "brooklynnets": {
                    "description": "Brooklyn Nets official team account",
                    "id": "18552281",
                    "type": "official"
               },
               "netsdaily": {
                    "description": "Account of SBNation blog for Brooklyn Nets fans",
                    "id": "39764121",
                    "type": "blog"
               }
          },
          "nba_nuggets": {
               "denvernuggets": {
                    "description": "Denver Nuggets official team account",
                    "id": "26074296",
                    "type": "official"
               },
               "denverstiffs": {
                    "description": "Account of SBNation blog for Denver Nuggets fans",
                    "id": "22037055",
                    "type": "blog"
               }
          },
          "nba_pacers": {
               "indycornrows": {
                    "description": "Account of SBNation blog for Indiana Pacers fans",
                    "id": "17859489",
                    "type": "blog"
               },
               "pacers": {
                    "description": "Indiana Pacers official team account",
                    "id": "19409270",
                    "type": "official"
               }
          },
          "nba_pelicans": {
               "pelicansnba": {
                    "description": "New Orleans Pelicans official team account",
                    "id": "24903350",
                    "type": "official"
               },
               "thebirdwrites": {
                    "description": "Account of SBNation blog for New Orleans Pelicans fans",
                    "id": "271676592",
                    "type": "blog"
               }
          },
          "nba_pistons": {
               "detroitbadboys": {
                    "description": "Account of SBNation blog for Detroit Pistons fans",
                    "id": "18560607",
                    "type": "blog"
               },
               "detroitpistons": {
                    "description": "Detroit Pistons official team account",
                    "id": "16727749",
                    "type": "official"
               }
          },
          "nba_raptors": {
               "raptors": {
                    "description": "Toronto Raptors official team account",
                    "id": "73406718",
                    "type": "official"
               },
               "raptorshq": {
                    "description": "Account of SBNation blog for Toronto Raptors fans",
                    "id": "2695011",
                    "type": "blog"
               }
          },
          "nba_rockets": {
               "dreamshakesbn": {
                    "description": "Account of SBNation blog for Houston Rockets fans",
                    "id": "236780729",
                    "type": "blog"
               },
               "houstonrockets": {
                    "description": "Houston Rockets official team account",
                    "id": "19077044",
                    "type": "official"
               }
          },
          "nba_spurs": {
               "poundingtherock": {
                    "description": "Account of SBNation blog for San Antonio Spurs fans",
                    "id": "38073084",
                    "type": "blog"
               },
               "spurs": {
                    "description": "San Antonio Spurs official team account",
                    "id": "18371803",
                    "type": "official"
               }
          },
          "nba_suns": {
               "brightsidesun": {
                    "description": "Account of SBNation blog for Phoenix Suns fans",
                    "id": "44136937",
                    "type": "blog"
               },
               "suns": {
                    "description": "Phoenix Suns official team account",
                    "id": "18481113",
                    "type": "official"
               }
          },
          "nba_thunder": {
               "okcthunder": {
                    "description": "Oklahoma Thunder official team account",
                    "id": "24925573",
                    "type": "official"
               },
               "wtlc": {
                    "description": "Account of SBNation blog for Oklahoma City Thunder fans",
                    "id": "18614809",
                    "type": "blog"
               }
          },
          "nba_timberwolves": {
               "canishoopus": {
                    "description": "Account of SBNation blog for Minnesota Timberwolves fans",
                    "id": "16521255",
                    "type": "blog"
               },
               "mntimberwolves": {
                    "description": "Minnesota Timberwolves official team account",
                    "id": "20196159",
                    "type": "official"
               }
          },
          "nba_trailblazers": {
               "blazersedge": {
                    "description": "Account of SBNation blog for Portland Trail Blazers fans",
                    "id": "2240416472",
                    "type": "blog"
               },
               "trailblazers": {
                    "description": "Portland Trail Blazers official team account",
                    "id": "6395222",
                    "type": "official"
               }
          },
          "nba_warriors": {
               "unstoppablebaby": {
                    "description": "Account of SBNation blog for Golden St. Warriors fans",
                    "id": "19683038",
                    "type": "blog"
               },
               "warriors": {
                    "description": "Golden St. Warriors official team account",
                    "id": "26270913",
                    "type": "official"
               }
          },
          "nba_wizards": {
               "bulletsforever": {
                    "description": "Account of SBNation blog for Washinton Wizards fans",
                    "id": "138771648",
                    "type": "blog"
               },
               "washwizards": {
                    "description": "Washinton Wizards official team account",
                    "id": "14992591",
                    "type": "official"
               }
          }
     },
     "nfl": {
          "nfl_49ers": {
               "49ers": {
                    "description": "San Francisco 49ers official team account",
                    "id": "43403778",
                    "type": "official"
               },
               "ninersnation": {
                    "description": "Account of SBNation blog for San Francisco 49ers fans",
                    "id": "17821827",
                    "type": "blog"
               }
          },
          "nfl_bears": {
               "chicagobears": {
                    "description": "Chicago Bears official team account",
                    "id": "47964412",
                    "type": "official"
               },
               "windycgridiron": {
                    "description": "Account of SBNation blog for Chicago Bears fans",
                    "id": "91252170",
                    "type": "blog"
               }
          },
          "nfl_bengals": {
               "bengals": {
                    "description": "Cincinnati Bengals official team account",
                    "id": "24179879",
                    "type": "official"
               },
               "cincyjungle": {
                    "description": "Account of SBNation blog for Cincinnati Bengals fans",
                    "id": "19627204",
                    "type": "blog"
               }
          },
          "nfl_bills": {
               "buffalobills": {
                    "description": "Buffalo Bills official team account",
                    "id": "25084916",
                    "type": "official"
               },
               "buffrumblings": {
                    "description": "Account of SBNation blog for Buffalo Bills fans",
                    "id": "21119156",
                    "type": "blog"
               }
          },
          "nfl_broncos": {
               "broncos": {
                    "description": "Denver Broncos official team account",
                    "id": "18734310",
                    "type": "official"
               },
               "milehighreport": {
                    "description": "Account of SBNation blog for Denver Broncos fans",
                    "id": "14583608",
                    "type": "blog"
               }
          },
          "nfl_browns": {
               "browns": {
                    "description": "Cleveland Browns official team account",
                    "id": "40358743",
                    "type": "official"
               },
               "dawgsbynature": {
                    "description": "Account of SBNation blog for Cleveland Browns fans",
                    "id": "115403866",
                    "type": "blog"
               }
          },
          "nfl_buccaneers": {
               "bucs_nation": {
                    "description": "Account of SBNation blog for Tampa Bay Buccaneers fans",
                    "id": "55322372",
                    "type": "blog"
               },
               "tbbuccaneers": {
                    "description": "Tampa Bay Buccaneers official team account",
                    "id": "36155311",
                    "type": "official"
               }
          },
          "nfl_cardinals": {
               "azcardinals": {
                    "description": "Arizona cardinals official team account",
                    "id": "389038362",
                    "type": "official"
               },
               "revengeofbirds": {
                    "description": "Account of SBNation blog for Arizona Cardinals fans",
                    "id": "262478611",
                    "type": "blog"
               }
          },
          "nfl_chargers": {
               "bftb_chargers": {
                    "description": "Account of SBNation blog for San Diego Chargers fans",
                    "id": "24868811",
                    "type": "blog"
               },
               "chargers": {
                    "description": "San Diego Chargers official team account",
                    "id": "713143",
                    "type": "official"
               }
          },
          "nfl_chiefs": {
               "arrowheadpride": {
                    "description": "Account of SBNation blog for Kansas City Chiefs fans",
                    "id": "24216003",
                    "type": "blog"
               },
               "kcchiefs": {
                    "description": "Kansas City Chiefs official team account",
                    "id": "33583496",
                    "type": "official"
               }
          },
          "nfl_colts": {
               "colts": {
                    "description": "Indianapolis Colts official team account",
                    "id": "180884045",
                    "type": "official"
               },
               "stampedeblue": {
                    "description": "Account of SBNation blog for Indianapolis Colts fans",
                    "id": "2645299910",
                    "type": "blog"
               }
          },
          "nfl_cowboys": {
               "bloggingtheboys": {
                    "description": "Account of SBNation blog for Dallas Cowboys fans",
                    "id": "18063523",
                    "type": "blog"
               },
               "dallascowboys": {
                    "description": "Dallas Cowboys official team account",
                    "id": "8824902",
                    "type": "official"
               }
          },
          "nfl_dolphins": {
               "miamidolphins": {
                    "description": "Miami Dolphins official team account",
                    "id": "19853312",
                    "type": "official"
               },
               "thephinsider": {
                    "description": "Account of SBNation blog for Miami Dolphins fans",
                    "id": "35398758",
                    "type": "blog"
               }
          },
          "nfl_eagles": {
               "bleedinggreen": {
                    "description": "Account of SBNation blog for Philadelphia Eagles fans",
                    "id": "20895801",
                    "type": "blog"
               },
               "eagles": {
                    "description": "Philadelphia Eagles official team account",
                    "id": "180503626",
                    "type": "official"
               }
          },
          "nfl_falcons": {
               "atlanta_falcons": {
                    "description": "Atlanta Falcons official team account",
                    "id": "16347506",
                    "type": "official"
               },
               "thefalcoholic": {
                    "description": "Account of SBNation blog for Atlanta Falcons fans",
                    "id": "22641709",
                    "type": "blog"
               }
          },
          "nfl_giants": {
               "bigblueview": {
                    "description": "Account of SBNation blog for New York Giants fans",
                    "id": "18197991",
                    "type": "blog"
               },
               "giants": {
                    "description": "New York Gians official team account",
                    "id": "240734425",
                    "type": "official"
               }
          },
          "nfl_jaguars": {
               "bigcatcountry": {
                    "description": "Account of SBNation blog for Jacksonville Jaguars fans",
                    "id": "12475622",
                    "type": "blog"
               },
               "jaguars": {
                    "description": "Jacksonville Jaguars official team account",
                    "id": "59471027",
                    "type": "official"
               }
          },
          "nfl_jets": {
               "ganggreennation": {
                    "description": "Account of SBNation blog for New York Jets fans",
                    "id": "19567338",
                    "type": "blog"
               },
               "nyjets": {
                    "description": "New York Jets official team account",
                    "id": "17076218",
                    "type": "official"
               }
          },
          "nfl_lions": {
               "lions": {
                    "description": "Detroit Lions official team account",
                    "id": "44666348",
                    "type": "official"
               },
               "prideofdetroit": {
                    "description": "Account of SBNation blog for Detroit Lions fans",
                    "id": "26681152",
                    "type": "blog"
               }
          },
          "nfl_packers": {
               "acmepackingco": {
                    "description": "Account of SBNation blog for Green Bay Packers fans",
                    "id": "42970928",
                    "type": "blog"
               },
               "packers": {
                    "description": "Green Bay Packers official team account",
                    "id": "35865630",
                    "type": "official"
               }
          },
          "nfl_panthers": {
               "catscratchreadr": {
                    "description": "Account of SBNation blog for Carolina Panthers fans",
                    "id": "27707480",
                    "type": "blog"
               },
               "panthers": {
                    "description": "Carolina Panthers official team account",
                    "id": "56443153",
                    "type": "official"
               }
          },
          "nfl_patriots": {
               "patriots": {
                    "description": "New England Patriots official team account",
                    "id": "31126587",
                    "type": "official"
               },
               "patspulpit": {
                    "description": "Account of SBNation blog for New England Patriots fans",
                    "id": "25698944",
                    "type": "blog"
               }
          },
          "nfl_raiders": {
               "raiders": {
                    "description": "Oakland Raiders official team account",
                    "id": "16332223",
                    "type": "official"
               },
               "silverblakpride": {
                    "description": "Account of SBNation blog for Oakland Raiders fans",
                    "id": "31194771",
                    "type": "blog"
               }
          },
          "nfl_rams": {
               "stlouisrams": {
                    "description": "St. Louis Rams official team account",
                    "id": "24109979",
                    "type": "official"
               },
               "turfshowtimes": {
                    "description": "Account of SBNation blog for St. Louis Rams fans",
                    "id": "17543615",
                    "type": "blog"
               }
          },
          "nfl_ravens": {
               "bmorebeatdown": {
                    "description": "Account of SBNation blog for Baltimore Ravens fans",
                    "id": "21424966",
                    "type": "blog"
               },
               "ravens": {
                    "description": "Baltimore Ravens official team account",
                    "id": "22146282",
                    "type": "official"
               }
          },
          "nfl_redskins": {
               "hogshaven": {
                    "description": "Account of SBNation blog for Washington Redskins fans",
                    "id": "27637990",
                    "type": "blog"
               },
               "redskins": {
                    "description": "Washington Redskins official team account",
                    "id": "36375662",
                    "type": "official"
               }
          },
          "nfl_saints": {
               "saints": {
                    "description": "New Orleans Saints official team account",
                    "id": "31504542",
                    "type": "official"
               },
               "saintscsc": {
                    "description": "Account of SBNation blog for New Orleans Saints fans",
                    "id": "44918020",
                    "type": "blog"
               }
          },
          "nfl_seahawks": {
               "fieldgulls": {
                    "description": "Account of SBNation blog for Seattle Seahawks fans",
                    "id": "23483385",
                    "type": "blog"
               },
               "seahawks": {
                    "description": "Seattle Seahawks official team account",
                    "id": "23642374",
                    "type": "official"
               }
          },
          "nfl_steelers": {
               "btsteelcurtain": {
                    "description": "Account of SBNation blog for Pittsburgh Steelers fans",
                    "id": "20337419",
                    "type": "blog"
               },
               "steelers": {
                    "description": "Pittsburgh Steelers official team account",
                    "id": "19426729",
                    "type": "official"
               }
          },
          "nfl_texans": {
               "battleredblog": {
                    "description": "Account of SBNation blog for Houston Texans fans",
                    "id": "17898886",
                    "type": "blog"
               },
               "houstontexans": {
                    "description": "Houston Texans official team account",
                    "id": "18336787",
                    "type": "official"
               }
          },
          "nfl_titans": {
               "tennesseetitans": {
                    "description": "Tennessee Titans official team account",
                    "id": "19383279",
                    "type": "official"
               },
               "titansmcm": {
                    "description": "Account of SBNation blog for Tennessee Titans fans",
                    "id": "16905915",
                    "type": "blog"
               }
          },
          "nfl_vikings": {
               "dailynorseman": {
                    "description": "Account of SBNation blog for Minnesota Vikings fans",
                    "id": "233129313",
                    "type": "blog"
               },
               "vikings": {
                    "description": "Minnesota Vikings official team account",
                    "id": "25545388",
                    "type": "official"
               }
          }
     },
     "nhl": {
          "nhl_avalanche": {
               "avalanche": {
                    "description": "Colorado Avalanche official team account",
                    "id": "26577824",
                    "type": "official"
               },
               "milehighhockey": {
                    "description": "Account of SBNation blog for Colorado Avalanche fans",
                    "id": "25867420",
                    "type": "blog"
               }
          },
          "nhl_blackhawks": {
               "2ndcityhockey": {
                    "description": "Account of SBNation blog for Chicago Blackhawks fans",
                    "id": "757214310",
                    "type": "blog"
               },
               "nhlblackhawks": {
                    "description": "Chicago Blackhawks official team account",
                    "id": "14498484",
                    "type": "official"
               }
          },
          "nhl_bluejackets": {
               "bluejacketsnhl": {
                    "description": "Columbus Blue Jackets official team account",
                    "id": "23783692",
                    "type": "official"
               },
               "cbjcannon": {
                    "description": "Account of SBNation blog for Columbus Blue Jackets fans",
                    "id": "21094092",
                    "type": "blog"
               }
          },
          "nhl_blues": {
               "stlouisblues": {
                    "description": "St. Louis Blues official team account",
                    "id": "22976125",
                    "type": "official"
               },
               "stlouisgametime": {
                    "description": "Account of SBNation blog for St. Loius Blues fans",
                    "id": "21165851",
                    "type": "blog"
               }
          },
          "nhl_bruins": {
               "cupofchowdah": {
                    "description": "Account of SBNation blog for Boston Bruins fans",
                    "id": "27371493",
                    "type": "blog"
               },
               "nhlbruins": {
                    "description": "Boston Bruins official team account",
                    "id": "44166798",
                    "type": "official"
               }
          },
          "nhl_canadiens": {
               "canadiensmtl": {
                    "description": "Montreal Canadiens official team account",
                    "id": "19678937",
                    "type": "official"
               },
               "habseotp": {
                    "description": "Account of SBNation blog for Montreal Canadiens fans",
                    "id": "196380056",
                    "type": "blog"
               }
          },
          "nhl_canucks": {
               "nucksmisconduct": {
                    "description": "Account of SBNation blog for Vancouver Canucks fans",
                    "id": "14550149",
                    "type": "blog"
               },
               "vancanucks": {
                    "description": "Vancouver Canucks official team account",
                    "id": "17093604",
                    "type": "official"
               }
          },
          "nhl_capitals": {
               "japersrink": {
                    "description": "Account of SBNation blog for Washington Capitals fans",
                    "id": "16498112",
                    "type": "blog"
               },
               "washcaps": {
                    "description": "Washington Capitals official team account",
                    "id": "14801539",
                    "type": "official"
               }
          },
          "nhl_coyotes": {
               "arizonacoyotes": {
                    "description": "Arizona Coyotes official team account",
                    "id": "20006987",
                    "type": "official"
               },
               "five4howling": {
                    "description": "Account of SBNation blog for Arizona Coyotes fans",
                    "id": "20814549",
                    "type": "blog"
               }
          },
          "nhl_devils": {
               "inlouwetrust": {
                    "description": "Account of SBNation blog for New Jersey Devils fans",
                    "id": "155301671",
                    "type": "blog"
               },
               "nhldevils": {
                    "description": "New Jersey Devils official team account",
                    "id": "40878677",
                    "type": "official"
               }
          },
          "nhl_ducks": {
               "anaheimcalling": {
                    "description": "Account of SBNation blog for Anaheim Ducks fans",
                    "id": "83889292",
                    "type": "blog"
               },
               "anaheimducks": {
                    "description": "Anaheim Ducks official team account",
                    "id": "19835035",
                    "type": "official"
               }
          },
          "nhl_flames": {
               "matchstickscgy": {
                    "description": "Account of SBNation blog for Calgary Flames fans",
                    "id": "252450271",
                    "type": "blog"
               },
               "nhlflames": {
                    "description": "Calgary Flames official team account",
                    "id": "27487343",
                    "type": "official"
               }
          },
          "nhl_flyers": {
               "broadsthockey": {
                    "description": "Account of SBNation blog for Philadelphia Flyers fans",
                    "id": "20225770",
                    "type": "blog"
               },
               "nhlflyers": {
                    "description": "Philadelphia Flyers official team account",
                    "id": "19618527",
                    "type": "official"
               }
          },
          "nhl_hurricanes": {
               "canescountry": {
                    "description": "Account of SBNation blog for Carolina Hurricanes fans",
                    "id": "17537200",
                    "type": "blog"
               },
               "nhlcanes": {
                    "description": "Carolina Hurricanes official team account",
                    "id": "19673276",
                    "type": "official"
               }
          },
          "nhl_islanders": {
               "lhhockey": {
                    "description": "Account of SBNation blog for New York Islanders fans",
                    "id": "17080778",
                    "type": "blog"
               },
               "nyislanders": {
                    "description": "New York Islanders official team account",
                    "id": "16651754",
                    "type": "official"
               }
          },
          "nhl_jets": {
               "arcticicehockey": {
                    "description": "Account of SBNation blog for Winnipeg Jets fans",
                    "id": "311783466",
                    "type": "blog"
               },
               "nhljets": {
                    "description": "Winnipeg Jets official team account",
                    "id": "308556440",
                    "type": "official"
               }
          },
          "nhl_kings": {
               "jftc_kings": {
                    "description": "Account of SBNation blog for Los Angeles Kings fans",
                    "id": "543794087",
                    "type": "blog"
               },
               "lakings": {
                    "description": "Los Angeles Kings official team account",
                    "id": "19013887",
                    "type": "official"
               }
          },
          "nhl_lightning": {
               "rawcharge": {
                    "description": "Account of SBNation blog for Tampa Bay Lightning fans",
                    "id": "43922115",
                    "type": "blog"
               },
               "tblightning": {
                    "description": "Tampa Bay Lightning official team account",
                    "id": "28173550",
                    "type": "official"
               }
          },
          "nhl_mapleleafs": {
               "mapleleafs": {
                    "description": "Toronto Maple Leafs official team account",
                    "id": "55594930",
                    "type": "official"
               },
               "mlse": {
                    "description": "Account of SBNation blog for Toronto Maple Leafs fans",
                    "id": "16440110",
                    "type": "blog"
               }
          },
          "nhl_oilers": {
               "copperandblue": {
                    "description": "Account of SBNation blog for Edmonton Oilers fans",
                    "id": "54653547",
                    "type": "blog"
               },
               "edmontonoilers": {
                    "description": "Edmonton Oilers official team account",
                    "id": "15361389",
                    "type": "official"
               }
          },
          "nhl_panthers": {
               "flapanthers": {
                    "description": "Florida Panthers official team account",
                    "id": "29460627",
                    "type": "official"
               },
               "litterboxcats": {
                    "description": "Account of SBNation blog for Florida Panthers fans",
                    "id": "16779721",
                    "type": "blog"
               }
          },
          "nhl_penguins": {
               "penguins": {
                    "description": "Pittsburgh Penguins official team account",
                    "id": "15020865",
                    "type": "official"
               },
               "pensburgh": {
                    "description": "Account of SBNation blog for Pittsburgh Penguins fans",
                    "id": "17064814",
                    "type": "blog"
               }
          },
          "nhl_predators": {
               "ontheforecheck": {
                    "description": "Account of SBNation blog for Nashville Predators fans",
                    "id": "2252615174",
                    "type": "blog"
               },
               "predsnhl": {
                    "description": "Nashville Predators official team account",
                    "id": "29264626",
                    "type": "official"
               }
          },
          "nhl_rangers": {
               "blueshirtbanter": {
                    "description": "Account of SBNation blog for New York Rangers fans",
                    "id": "32262639",
                    "type": "blog"
               },
               "nyrangers": {
                    "description": "New York Rangers official team account",
                    "id": "20264905",
                    "type": "official"
               }
          },
          "nhl_redwings": {
               "detroitredwings": {
                    "description": "Detroit Red Wings official team account",
                    "id": "16826656",
                    "type": "official"
               },
               "wingingitmotown": {
                    "description": "Account of SBNation blog for Detroit Red Wings fans",
                    "id": "50778210",
                    "type": "blog"
               }
          },
          "nhl_sabres": {
               "buffalosabres": {
                    "description": "Buffalo Sabres official team account",
                    "id": "22536395",
                    "type": "official"
               },
               "diebytheblade": {
                    "description": "Account of SBNation blog for Buffalo Sabres fans",
                    "id": "17059046",
                    "type": "blog"
               }
          },
          "nhl_senators": {
               "senators": {
                    "description": "Ottowa Senators official team account",
                    "id": "43885373",
                    "type": "official"
               },
               "silversevensens": {
                    "description": "Account of SBNation blog for Ottowa Senators fans",
                    "id": "27501156",
                    "type": "blog"
               }
          },
          "nhl_sharks": {
               "fearthefin": {
                    "description": "Account of SBNation blog for San Jose Sharks fans",
                    "id": "23126410",
                    "type": "blog"
               },
               "sanjosesharks": {
                    "description": "San Jose Sharks official team account",
                    "id": "27961547",
                    "type": "official"
               }
          },
          "nhl_stars": {
               "dallasstars": {
                    "description": "Dallas Stars official team account",
                    "id": "29304837",
                    "type": "official"
               },
               "defendingbigd": {
                    "description": "Account of SBNation blog for Dallas Stars fans",
                    "id": "18395755",
                    "type": "blog"
               }
          },
          "nhl_wild": {
               "hockeywildernes": {
                    "description": "Account of SBNation blog for Minnesota Wild fans",
                    "id": "16426969",
                    "type": "blog"
               },
               "mnwild": {
                    "description": "Minnesota Wild official team account",
                    "id": "17374906",
                    "type": "official"
               }
          }
     }
}


# Specification of DB views
# * Each list element represents a view. For each view list: 
#   - First element is the NAME OF THE VIEW
#   - Second element is the SQL TO CREATE THE VIEW
DB_VIEWS = [
    [
    'sentiment',
    'SELECT s.tw_text, t.tw_sent_polarity, t.tw_sent_subjectivity FROM sentiment_check AS s INNER JOIN tweets AS t ON s.tweet_id = t.tw_id_str'
    ]
]
