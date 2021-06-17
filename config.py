from sqlalchemy import create_engine


def get_config():
    engine = create_engine(
        "mssql+pyodbc://sa:123456@192.168.1.79/auto_database?driver=ODBC+Driver+13+for+SQL+Server",
        fast_executemany=True)
    return engine
