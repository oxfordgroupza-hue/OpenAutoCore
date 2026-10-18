"""Central API database connection factory.

Connections are opened only when a request invokes the factory. Keep database
credentials in deployment environment variables, never in source control.
"""
from __future__ import annotations

import os
import mysql.connector


def connect_db():
    required = ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_NAME")
    if any(not os.getenv(name) for name in required):
        raise RuntimeError("Central API database configuration is incomplete")
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_NAME"],
        connection_timeout=10,
        autocommit=False,
        charset="utf8mb4",
        use_unicode=True,
    )
