from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, inspect, func
from datetime import datetime, time, timedelta
import config


Base = automap_base()
engine = config.get_config()
SessionSql = sessionmaker()
SessionSql.configure(bind=engine)
Base.prepare(engine, reflect=True)

COLOR = Base.classes.COLOR


def color_add(color_name=None, color_name_en = None):
    session_sql = SessionSql()
    error_code = 1
    if color_name is not None:
        rs_id_max = session_sql.query(func.max(COLOR.COLOR_ID))
        get_id = rs_id_max.all()[0][0]
        if get_id == None:
            color_id = 0
        else:
            color_id = int(get_id) + 1
        if color_name_en is None:
            json_insert = {
                'COLOR_ID': color_id,
                'COLOR_NAME':color_name
            }
        else:
            json_insert = {
                'COLOR_ID': color_id,
                'COLOR_NAME': color_name,
                'COLOR_NAME_EN': color_name_en
            }
        try:
            obj = COLOR(**json_insert)
            session_sql.add(obj)
            session_sql.commit()
            error_code = 0
        except:
            error_code = 1

    session_sql.close()
    return error_code

