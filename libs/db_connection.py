# import required module - working with SQLAlchemy,
# mysql.connector is deprecated and will be removed in future
import sqlalchemy as db
from urllib.parse import quote_plus as urlquote

# Simple connector to dbase
# Loads database credits and returns connection
# You should add the error reporting!
def db_connector():
    engine = db.create_engine('mysql+pymysql://user:%s@host/db_name' % urlquote('pass'))
    connection = engine.connect()
    return connection    
