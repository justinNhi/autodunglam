import jwt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, inspect, func, cast, Numeric, VARBINARY, types, update, insert
from datetime import datetime, time, timedelta, date
import config
import binascii
import uuid
import hashlib

Base = automap_base()
engine = config.get_config()
SessionSql = sessionmaker()
SessionSql.configure(bind=engine)
Base.prepare(engine, reflect=True)
USER = Base.classes.USER
USER_LOG = Base.classes.USER_LOG
# USER_WEB_FUNCTION = Base.classes.USER_WEB_FUNCTION
USER_USER_GROUP_RELATIONSHIP = Base.classes.USER_USER_GROUP_RELATIONSHIP
USER_GROUP = Base.classes.USER_GROUP
# USER_GROUP_USER_MODULE_RELATIONSHIP =  Base.classes.USER_GROUP_USER_MODULE_RELATIONSHIP
# USER_MODULE = Base.classes.USER_MODULE
# USER_MODULE_FUNCTION_RELATIONSHIP = Base.classes.USER_MODULE_FUNCTION_RELATIONSHIP
# FUNCTION = Base.classes.FUNCTION
#
# USER_cols = USER.__table__.columns.keys()
# USER_LOG_cols = USER_LOG.__table__.columns.keys()
# USER_WEB_FUNCTION_cols = USER_WEB_FUNCTION.__table__.columns.keys()
# # USER_USER_GROUP_REALATIONSHOP_cols = USER_USER_GROUP_REALATIONSHIP.__table__.columns.keys()
# USER_GROUP_cols = USER_GROUP.__table__.columns.keys()
# # USER_GROUP_USER_MODULE_RELATIONSHIP_cols = USER_GROUP_USER_MODULE_RELATIONSHIP.__table__.columns.keys()
# USER_MODULE_cols = USER_MODULE.__table__.columns.keys()
# USER_MODULE_FUNCTION_REALATIONSHOP_cols = USER_MODULE_FUNCTION_RELATIONSHIP.__table__.columns.keys()
# FUNCTION_cols = FUNCTION.__table__.columns.keys()

def get_max_id(TABLE_NAME):
    session_sql = SessionSql()
    rs_user_id_max = session_sql.query(func.max(TABLE_NAME))
    get_id = rs_user_id_max.all()[0][0]
    if get_id == None:
        id_max = 1
    else:
        id_max = int(get_id) + 1
    session_sql.close()
    return id_max



# user

def user_add(guest_id=None, user_name=None, user_password=None, user_token=None,
             create_user_id=None, user_status=None):
    session_sql = SessionSql()
    error_code = 1
    if user_name is not None and user_password is not None:
        json_insert = {}
        password = bytes(str(user_password), "utf-8")
        json_insert['USER_PASSWORD'] = cast(password, VARBINARY(100))
        json_insert['USER_NAME'] = str(user_name)
        user_id = get_max_id(USER.USER_ID)
        json_insert['USER_ID'] = user_id
        if guest_id is not None:
            json_insert['GUEST_ID'] = guest_id
        if user_token is not None:
            json_insert['USER_TOKEN'] = user_token
        if create_user_id is not None:
            json_insert['CREATE_USER_ID'] = create_user_id
        if user_status is not None:
            json_insert['USER_STATUS'] = user_status
        try:
            obj = USER(**json_insert)
            session_sql.add(obj)
            session_sql.commit()
            error_code = 0
        except:
            error_code = 1

    session_sql.close()
    return error_code


def user_login(user_name, user_password, key, ip_user, browser_name):
    session_sql = SessionSql()
    password = bytes(str(user_password), "utf-8")
    try:
        rs_login = session_sql.query(USER).\
            filter(USER.USER_NAME == user_name, USER.USER_PASSWORD == cast(password,VARBINARY(100)))
        check_login = len(rs_login.all())
        if check_login == 1:
            rs_user_group = session_sql.query(USER_GROUP, USER_USER_GROUP_RELATIONSHIP).\
                filter(USER_USER_GROUP_RELATIONSHIP.USER_ID == getattr(rs_login.all()[0], 'USER_ID'))
            date_timeout = (date.today() + timedelta(days=1)).strftime("%m/%d/%Y")
            json_send = {
                "USER_NAME": user_name,
                'USER_ID' : str(getattr(rs_login.all()[0], 'USER_ID')),
                'USER_GROUP_ID': str(getattr(rs_user_group.all()[0][0], 'USER_GROUP_ID')),
                'USER_GROUP_NAME': getattr(rs_user_group.all()[0][0], 'USER_GROUP_NAME'),
                'TIME_OUT': date_timeout
            }
            token = jwt.encode(
                json_send,
                key
            )
            error_code = 0
            user_group_id = int(getattr(rs_user_group.all()[0][0], "USER_GROUP_ID"))
            try:
                json_log = {
                    "USER_NAME": user_name,
                    "USER_ID": str(getattr(rs_login.all()[0], 'USER_ID')),
                    "USER_IP_ADDRESS": ip_user,
                    "USER_USED_BROWSER": browser_name,
                    "USER_LAST_LOGIN": datetime.today()
                }
                user_log_add(json_log)
            except:
                pass
        else:
            error_code = 1
            user_group_id = None
            token = None
    except:
        error_code = 1
        user_group_id = None
        token = None
    return [error_code, user_group_id, token]


def user_log_add(json_log):
    session_sql = SessionSql()
    try:
        obj = USER_LOG(**json_log)
        session_sql.add(obj)
        session_sql.commit()
    except:
        pass
    session_sql.close()