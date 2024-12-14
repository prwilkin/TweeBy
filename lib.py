import sqlite3, logging, tweepy, os
import sys

# Create and configure logger
logging.basicConfig(filename="newfile.log", format='%(asctime)s %(message)s', filemode='w')
# Creating an object
logger = logging.getLogger()
logger.setLevel(logging.INFO)


try:
    sqliteConnection = sqlite3.connect('sql.db')
    cursor = sqliteConnection.cursor()
    logger.info('Database Initialized Successfully')
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
    sqliteConnection.commit()  # Save the changes
    logger.info("Table 'mappings' created successfully")

    db = cursor


auth = tweepy.auth.OAuth2BearerHandler(os.environ['TWITTER_TOKEN'])
twit = tweepy.API(auth)


def close(error=False):
    db.close()
    sqliteConnection.close()
    if error is False:
        sys.exit(0)
    else:
        sys.exit(1)
