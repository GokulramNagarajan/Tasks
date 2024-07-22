"""This module provides a reference implementation of a consumer of the `lfb-rt-simulator` service.
Steps implemented by the consumer:
- read events from the `lfb-rt-simulator` websocket at LFB_RT_SIMULATOR_URI
- store events in the `lfb.incidents` table (in a Postgres database running on POSTGRES_HOSTNAME)
"""
import json
import os
from pathlib import Path
import pgsql

from websocket import create_connection

LFB_RT_SIMULATOR_URI = os.environ.get("LFB_RT_SIMULATOR_URI")
POSTGRES_HOSTNAME = os.environ.get("POSTGRES_HOSTNAME")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")


def consume_data():
    """Read records from `LFB_RT_SIMULATOR_URI` websocket and insert them into
    the `incidents` table in the `lfb` Postgres database.
    The execution completes when the websocket has no more records to serve. 
    """
    uri = LFB_RT_SIMULATOR_URI
    db_connection = pgsql.Connection(
        (POSTGRES_HOSTNAME, POSTGRES_PORT),
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB)
    setup_db(db_connection)
    ws_connection = create_connection(LFB_RT_SIMULATOR_URI)
    insert_statement_template = load_insert_statement_template()
    payload = ws_connection.recv()
    while payload:
        payload_utf8 = payload.decode()
        record_json = json.loads(payload_utf8)
        print("Inserting IncidentNumber={IncidentNumber}".format(IncidentNumber=record_json["IncidentNumber"]))
        insert_statement = generate_insert_statement(insert_statement_template, record_json)
        print(insert_statement)
        db_connection(insert_statement)
        payload =  ws_connection.recv()
    ws_connection.close()

def setup_db(connection: pgsql.Connection):
    """Reset (truncate) the `incidents` table.

    Args:
        connection (pgsql.Connection): connection to the Postgres dataabase
    """
    connection("TRUNCATE TABLE incidents;")
    print("Table incidents truncated.")

def load_insert_statement_template() -> str:
    """Load the INSERT statement template from
    `sql/lfb-incidents-insert.sql` file and returns it in
    a string.
    The template string can be filled with `str.format()`.
    Variables in the template string are named like columns in
    `incidents` table with the only difference of
    'Notional Cost (£)' whose variable is named `Notional_Cost`.

    Returns:
        str: the INSERT statement template
    """
    insert_stmt_file_path = Path(__file__).parent / "sql/lfb-incidents-insert.sql"
    with open(insert_stmt_file_path, "r") as insert_stmt_template_file:
        insert_stmt_template = insert_stmt_template_file.read()
    return insert_stmt_template

def generate_insert_statement(template: str, record: dict) -> str:
    """Generate the INSERT statement that will insert a new row into
    `lfb.incidents` table with the values from `record`.
    
    Args:
        template (str): the template INSERT string
        record (dict): a dictionary containing the values to be inserted

    Returns:
        str: an INSERT statement with values from `record`
    """
    # rename the column to ease the building of the insert stmt
    record["Notional_Cost"] = record["Notional Cost (£)"]
    return template.format(**record)

if __name__ == "__main__":
    consume_data()
