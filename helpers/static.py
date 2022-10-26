# Main static values
VERSION_NUMBER = "X.X"
DATA_FOLDER_NAME = "data"
LOG_FOLDER_NAME = "logs"
DEBUG_LEVEL = 20
MAX_DEPTH = 3
PROTOCOL_KEYWORDS = ["https://", "http://"]
AMP_KEYWORDS = ["/amp", "amp/", ".amp", "amp.", "?amp", "amp?", "=amp",
                "amp=", "&amp", "amp&", "%amp", "amp%", "_amp", "amp_"]
DENYLISTED_DOMAINS = ["bandcamp.com",
                      "progonlymusic.com", "spotify.com", "youtube.com"]

# Reddit API credentials for PRAW
USERNAME = "RedditUsername"
PASSWORD = "RedditPassword"
CLIENT_ID = "RedditClientId"
CLIENT_SECRET = "RedditClientSecret"
USER_AGENT = f"HostingPlatform:{USERNAME}:v{VERSION_NUMBER} (by CreatorUsername)"

# Twitter API credentials for Tweepy
TW_API_KEY = "TwitterAPIKey"
TW_API_SECRET_KEY = "TwitterAPISecretKey"
TW_ACCESS_TOKEN = "TwitterAccessToken"
TW_ACCESS_TOKEN_SECRET = "TwitterAccessTokenSecret"

# The user-agents below are just examples, you have to change them before you run the scripts.
# Only use mobile user-agents that are new, common and not block-listed.
# This will prevent 403-errors and allow you to scrape more websites.
HEADERS = ['Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3202.84 Mobile Safari/537.36',
           'Mozilla/5.0 (Linux; Android 9; CLT-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3945.116 Mobile Safari/537.36']

# SSH credentials
SSH_HOSTNAME = "SshHostname"
SSH_USERNAME = "SshUsername"
SSH_PASSWORD = "SshPassword"
SSH_SSH_TIMEOUT = X.X
SSH_TUNNEL_TIMEOUT = X.X

# Database credentials
DB_USERNAME = "DbUsername"
DB_PASSWORD = "DbPassword"
DB_HOSTNAME = "DbHostname"
DB_DATABASENAME = "DbDatabasename"
DB_SERVER_PORT = 1234
DB_LOCAL_PORT = "123.4.5.6"

# Pages
FAQ_LINK = "LinkToFAQ"
SUMMON_INFO_LINK = "LinkToHowToSummon"
