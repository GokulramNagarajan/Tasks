"""This module provides an implementation of a websocket server that simulates the live generation
of fire incidents read from the "London Fire Brigade Incident Records - 2017 onwards" dataset
(https://data.london.gov.uk/dataset/london-fire-brigade-incident-records).

The websocket is running on port 5678.
Each event is a row from the dataset and it is published as a stringified UTF-8 encoded JSON object.
An excerpt of the event: '{"IncidentNumber": "000004-01012017", ..., "Notional Cost (\xc2\xa3)": "326"}'

The speed of the simulation is driven by the environment variable `PRODUCER_MAX_SLEEP_TIME_SECONDS`.
This variable specifies the maximum amount of seconds that the server can wait between the publishing 
of two events.
Set to 0 in order to force the server to flush all the events without waiting time.

Note: the server exports another websocket on port 5679. This websocket is used to determine if
the server is up and ready to serve events (it is used by Docker Compose healthcheck).
"""
import asyncio
import csv
import gzip
import json
import os
import random
import websockets

CSV_FILE_LOCATION = os.environ.get("CSV_FILE_LOCATION", None)
PRODUCER_MAX_SLEEP_TIME_SECONDS = int(os.environ.get("PRODUCER_MAX_SLEEP_TIME_SECONDS", None))

def print_log(websocket, data):
    srv_host = websocket.host
    srv_port = websocket.port
    destination_host = websocket.remote_address[0]
    destination_port = websocket.remote_address[1]
    print(f"[{srv_host}:{srv_port} -> {destination_host}:{destination_port}] {data}")

async def rt_simulator(websocket, _):
    gzip_file = gzip.open(CSV_FILE_LOCATION, mode="rt", encoding="utf-8-sig")
    dict_stream = csv.DictReader(gzip_file, delimiter=",")
    for row in dict_stream:
        data = json.dumps(row, ensure_ascii=False).encode("utf8")
        await websocket.send(data)
        print_log(websocket, data)
        # simulate a wait time of before sending the next row
        await asyncio.sleep(
            random.randint(0, PRODUCER_MAX_SLEEP_TIME_SECONDS)
        )

async def hello(websocket, _):
    data = "HELLO"
    await websocket.send(data)
    print_log(websocket, data)

lfb_data_server = websockets.serve(rt_simulator, "0.0.0.0", 5678)
health_check_server = websockets.serve(hello, "0.0.0.0", 5679)

asyncio.get_event_loop().run_until_complete(asyncio.gather(lfb_data_server, health_check_server))
asyncio.get_event_loop().run_forever()
