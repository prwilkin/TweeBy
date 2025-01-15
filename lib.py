import sqlite3, logging, tweepy, os, sys
from dotenv import load_dotenv


# Create and configure logger
logging.basicConfig(filename="main.log", format='%(asctime)s %(message)s', filemode='a')
# Creating an object
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


try:
    sqlconnection = sqlite3.connect('data/sql.db')
    cursor = sqlconnection.cursor()
    logger.debug('Database Initialized Successfully')
except sqlite3.Error as error:
    logger.error(f"Error while connecting to sqlite: {error}")
else:
    # SQL command to create table
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS ids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing unique ID
        blskyid TEXT NOT NULL,                 -- Bluesky post ID
        twitid TEXT NOT NULL                  -- Twitter post ID
    );
    '''

    cursor.execute(create_table_query)  # Execute the SQL query
    sqlconnection.commit()  # Save the changes
    logger.debug("Table 'ids' created successfully")

    db = cursor


class TwitterAPI:
    def __init__(self):
        load_dotenv()
        self.apiV2 = tweepy.Client(
            bearer_token=os.environ['TWITTER_TOKEN'],
            consumer_key=os.environ['TWITTER_CONSUMER_ID'],
            consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
            access_token=os.environ['TWITTER_ACCESS_TOKEN'],
            access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
        )
        auth = tweepy.OAuth2BearerHandler(os.environ['TWITTER_TOKEN'])
        # auth = tweepy.OAuth2AppHandler(
        #     consumer_key=os.environ['TWITTER_API_KEY'],
        #     consumer_secret=os.environ['TWITTER_API_SECRET'])
        self.apiV1 = tweepy.API(auth=auth)


twit = TwitterAPI()


def close(error=False):
    if sqlconnection:
        sqlconnection.close()
    if error is False:
        sys.exit(0)
    else:
        sys.exit(1)
