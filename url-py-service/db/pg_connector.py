import logging
from typing import Optional
import os
import psycopg2
from psycopg2 import sql



# LOGGING
logging.basicConfig(level=logging.DEBUG)
logging.debug("Debug message")


DB_HOST=os.getenv('DB_HOST')
DB_NAME="yourdbname"
DB_USER="yourusername"
DB_PASSWORD="yourpassword"
DB_PORT=5432



# Connect to the Postgres Database
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,  # yourdbname
        user=DB_USER,    # yourusername
        password=DB_PASSWORD,  # yourpassword
        host=DB_HOST,  # localhost or the correct host
        port=DB_PORT  # 5432
    )


def get_from_database(short_url: str) -> Optional[str]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT original_url, clicks 
            FROM urls 
            WHERE short_code = %s
            LIMIT 1
        """
        cursor.execute(query, (short_url,))
        result = cursor.fetchone()
        
        if result:
            original_url, clicks = result
            # Update click count
            cursor.execute(
                "UPDATE urls SET clicks = clicks + 1 WHERE short_code = %s",
                (short_url,)
            )
            conn.commit()
            return original_url
            
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
    
    return None