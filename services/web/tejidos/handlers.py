import json
import logging

from datetime import datetime
from typing import Any, Dict, cast, List, Union
from tejidos.util import dumps_json_to_s3, loads_json_from_s3, loads_csv_from_s3

def download_handler(_event: Any, _context: Any) -> None:

    logging.info("Download handler.")

    now = datetime.now()
    timestamp = datetime.timestamp(now)

    payload = json.dumps({"timestamp": timestamp})

    dumps_json_to_s3(body=payload, bucket="tejidos-data", key="input/timestamp.json")

def process_handler(event: Any, _context: Any) -> None:

    logging.info("Process handler.")

    record = event.get("Records")[0]
    s3_object = record.get("s3")
    bucket = s3_object.get("bucket").get("name")
    key = s3_object.get("object").get("key")


    data = loads_json_from_s3(bucket=bucket, key=key)
    date = datetime.fromtimestamp(cast(float, data.get("timestamp")))
    payload = json.dumps({"date": date.strftime("%m/%d/%Y, %H:%M:%S")})

    dumps_json_to_s3(body=payload, bucket="tejidos-data", key="output/datetime.txt")

def endpoint_handler(_event: Any, _context: Any) -> Dict:

    logging.info("Endpoint handler.")

    def transform(data: Union[List, str]) -> Union[List, int]:
        if isinstance(data, list):
            return [transform(element) for element in data]
        return int(float(data))

    return {"execution_time": loads_json_from_s3(bucket="tejidos-data",
                                                 key="output/datetime.txt"),
            "threading": transform(loads_csv_from_s3(bucket="tejidos-data",
                                                     key="output/threading.csv")),
            "tieup": transform(loads_csv_from_s3(bucket="tejidos-data",
                                                 key="output/tieup.csv")),
            "treadling": transform(loads_csv_from_s3(bucket="tejidos-data",
                                                     key="output/treadling.csv"))}
