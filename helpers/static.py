import os

# Main static values
MAX_DEPTH = 3
PROTOCOL_KEYWORDS = ["https://", "http://"]
AMP_KEYWORDS = ["/amp", "amp/", ".amp", "amp.", "?amp", "amp?", "=amp",
                "amp=", "&amp", "amp&", "%amp", "amp%", "_amp", "amp_"]
DENYLISTED_DOMAINS = ["bandcamp.com",
                      "progonlymusic.com", "spotify.com", "youtube.com"]

# The user-agents below are just examples, you have to change them before you run the scripts.
# Only use mobile user-agents that are new, common and not block-listed.
# This will prevent 403-errors and allow you to scrape more websites.
HEADERS = ['Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3202.84 Mobile Safari/537.36',
           'Mozilla/5.0 (Linux; Android 9; CLT-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3945.116 Mobile Safari/537.36']

# Database credentials
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOSTNAME = os.environ["DB_HOSTNAME"]
DB_DATABASENAME = os.environ["DB_DATABASENAME"]
