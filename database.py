from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import mysql.connector
import time
from logger import console_logger


def create_database():
    global db_created
    attempts = 1

    while attempts > 0:
        attempts -= 1
        time.sleep(2)
        try:
            mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Diycam#1234"
                )
            mycursor = mydb.cursor()
            if mydb.is_connected():
                # console_logger.debug("db_conected successfully")
                mycursor = mydb.cursor()
                mycursor.execute("SHOW DATABASES")
                dbExist = False
                db_created = False
                for x in mycursor:
                    if x[0] == "tasktest":
                        dbExist = True
                if not dbExist:
                    db_created = True
                    mycursor.execute("CREATE DATABASE tasktest")
                mycursor.execute("SHOW DATABASES")
                for x in mycursor:
                    if x[0] == "tasktest":
                        dbExist = True
                return dbExist
            return False
        except Exception as e:
            console_logger.debug("retrying db connection ...")
            console_logger.debug(e)
    return

def create_db_url():
    try:
        if create_database():
            return "mysql+pymysql://{}:{}@{}:{}/{}?max_allowed_packet=64M".format("root",
                                                                                  "Diycam#1234",
                                                                                  "localhost",
                                                                                  "3306",
                                                                                  "tasktest"
                                                                                  )
    except Exception as e:
        console_logger.debug(
            "database creation failed check mysql server connection and db credentials")
        return None

engine, Base, SessionLocal = None, None, None
db_instance = create_db_url()
if db_instance:
    engine = create_engine(db_instance, pool_recycle=280,
                           pool_pre_ping=True, pool_size=20,  max_overflow=-1, pool_use_lifo=True, connect_args={'connect_timeout': 10})
    SessionLocal = sessionmaker(bind=engine)
    Base = declarative_base()


def get_db():
    with SessionLocal() as db:
        try:
            return db
        finally:
            db.commit()
            db.close()
