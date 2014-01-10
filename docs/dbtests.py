"""
DB-related tests, separated from main unit tests because they need local database
setup prior to running.

"""

import sys
sys.path.insert(0, './src')
import petl
from petl.testutils import ieq
from petl import look, fromdb
from petlx.sql import todb


def exercise(dbo):
    print '=' * len(repr(dbo))
    print repr(dbo)
    print '=' * len(repr(dbo))
    print
    
    expect = (('foo', 'bar'), ('a', 1), ('b', 1))
    expect_extended = (('foo', 'bar', 'baz'), ('a', 1, 2.3), ('b', 1, 4.1))
    actual = fromdb(dbo, 'SELECT * FROM testx')

    print "verify table doesn't exist to start with"
    try:
        print look(actual)
    except Exception as e:
        print 'expected exception: ' + str(e)
    else:
        raise Exception('expected exception not raised')

    print "verify cannot write without create"
    try:
        todb(expect, dbo, 'testx')
    except Exception as e:
        print 'expected exception: ' + str(e)
    else:
        raise Exception('expected exception not raised')

    print 'create table and verify...'
    todb(expect, dbo, 'testx', create=True)
    ieq(expect, actual)
    print look(actual)
    
    print 'verify cannot overwrite with new cols without recreate...'
    try:
        todb(expect_extended, dbo, 'testx')
    except Exception as e:
        print 'expected exception: ' + str(e)
    else:
        raise Exception('expected exception not raised')
    
    print 'verify recreate...'
    todb(expect_extended, dbo, 'testx', create=True, drop=True)
    ieq(expect_extended, actual)
    print look(actual)


def setup_mysql(dbapi_connection):
    # setup table
    cursor = dbapi_connection.cursor()
    # deal with quote compatibility
    cursor.execute('SET SQL_MODE=ANSI_QUOTES')
    cursor.execute('DROP TABLE IF EXISTS testx')
    cursor.close()
    dbapi_connection.commit()


def exercise_mysql(host, user, passwd, db):
    import MySQLdb
    
    # assume database already created
    dbapi_connection = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    
    # exercise using a dbapi_connection
    setup_mysql(dbapi_connection)
    exercise(dbapi_connection)
    
    # exercise using a dbapi_cursor
    setup_mysql(dbapi_connection)
    dbapi_cursor = dbapi_connection.cursor()
    exercise(dbapi_cursor)
    dbapi_cursor.close()
    
    # exercise sqlalchemy dbapi_connection
    setup_mysql(dbapi_connection)
    from sqlalchemy import create_engine
    sqlalchemy_engine = create_engine('mysql://%s:%s@%s/%s' % (user, passwd, host, db))
    sqlalchemy_connection = sqlalchemy_engine.connect()
    sqlalchemy_connection.execute('SET SQL_MODE=ANSI_QUOTES')
    exercise(sqlalchemy_connection)
    sqlalchemy_connection.close()
    
    # exercise sqlalchemy session
    setup_mysql(dbapi_connection)
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=sqlalchemy_engine)
    sqlalchemy_session = Session()
    exercise(sqlalchemy_session)
    sqlalchemy_session.close()


def setup_postgresql(dbapi_connection):
    # setup table
    cursor = dbapi_connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS testx')
    cursor.close()
    dbapi_connection.commit()
    
    
def exercise_postgresql(host, user, passwd, db):
    import psycopg2
    
    # assume database already created
    dbapi_connection = psycopg2.connect('host=%s dbname=%s user=%s password=%s' % (host, db, user, passwd))
    dbapi_connection.autocommit = True

    # exercise using a dbapi_connection
    setup_postgresql(dbapi_connection)
    exercise(dbapi_connection)

    # exercise using a dbapi_cursor
    setup_postgresql(dbapi_connection)
    dbapi_cursor = dbapi_connection.cursor()
    exercise(dbapi_cursor)
    dbapi_cursor.close()

    # ignore these for now, having trouble with autocommit
    #
    # # exercise sqlalchemy dbapi_connection
    # setup_postgresql(dbapi_connection)
    # from sqlalchemy import create_engine
    # sqlalchemy_engine = create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (user, passwd, host, db))
    # sqlalchemy_connection = sqlalchemy_engine.connect()
    # exercise(sqlalchemy_connection)
    # sqlalchemy_connection.close()
    #
    # # exercise sqlalchemy session
    # setup_postgresql(dbapi_connection)
    # from sqlalchemy.orm import sessionmaker
    # Session = sessionmaker(bind=sqlalchemy_engine)
    # sqlalchemy_session = Session()
    # exercise(sqlalchemy_session)
    # sqlalchemy_session.close()


if __name__ == '__main__':
    print petl.VERSION
    
    # setup logging
    import logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(name)s - %(funcName)s - %(message)s')
    ch.setFormatter(formatter)
    logger = logging.getLogger('petl.io')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger = logging.getLogger('petlx.sql')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    
    if sys.argv[1] == 'mysql':
        exercise_mysql(*sys.argv[2:])
    elif sys.argv[1] == 'postgresql':
        exercise_postgresql(*sys.argv[2:])
    else:
        print 'either mysql or postgresql'
    
    
    
    
        
    
    
    
