import urllib
import pyodbc
from sqlalchemy import create_engine
from src.config.settings import (
    SQL_SERVER,
    SQL_DATABASE,
    SQL_DRIVER,
    SQL_TRUSTED_CONNECTION,
    SQL_TRUST_CERT,
    SQL_USER,
    SQL_PASSWORD
)

def get_connection_string(database: str = None) -> str:
    """Build ODBC connection string for SQL Server."""
    target_db = database if database else SQL_DATABASE
    conn_parts = [
        f"DRIVER={{{SQL_DRIVER}}}",
        f"SERVER={SQL_SERVER}",
        f"DATABASE={target_db}",
    ]
    if SQL_TRUSTED_CONNECTION.lower() == "yes":
        conn_parts.append("Trusted_Connection=yes")
    else:
        conn_parts.append(f"UID={SQL_USER}")
        conn_parts.append(f"PWD={SQL_PASSWORD}")
        
    if SQL_TRUST_CERT.lower() == "yes":
        conn_parts.append("TrustServerCertificate=yes")
        
    return ";".join(conn_parts) + ";"

def get_pyodbc_connection(database: str = None) -> pyodbc.Connection:
    """Get raw pyodbc connection."""
    conn_str = get_connection_string(database)
    return pyodbc.connect(conn_str, autocommit=True)

def get_sqlalchemy_engine(database: str = None):
    """Get SQLAlchemy Engine configured with fast_executemany."""
    conn_str = get_connection_string(database)
    params = urllib.parse.quote_plus(conn_str)
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        fast_executemany=True,
        pool_pre_ping=True
    )
    return engine
