import sqlite3, logging


def logger_connect():
    # Create and configure logger
    logging.basicConfig(filename="newfile.log", format='%(asctime)s %(message)s', filemode='w')
    # Creating an object
    global logger
    logger = logging.getLogger()


def db_connect():
    try:
        sqliteConnection = sqlite3.connect('sql.db')
        cursor = sqliteConnection.cursor()
        logger.info('Database Initialized Successfully')
    except sqlite3.Error as error:
        logger.error(f"Error while connecting to sqlite: {error}")
    else:
        # SQL command to create table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing unique ID
            blskyid TEXT NOT NULL,                 -- Bluesky post ID
            twitid TEXT NOT NULL                  -- Twitter post ID
        );
        '''
        cursor.execute(create_table_query)  # Execute the SQL query
        sqliteConnection.commit()  # Save the changes
        logger.info("Table 'mappings' created successfully")
        return cursor


def main():
    logger_connect()
    db = db_connect()



if __name__ == "__main__":
    main()