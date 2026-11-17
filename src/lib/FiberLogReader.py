import logging
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

Area = str

DOOR_OPEN_CODE = "[008]"
ANIMAL_OUT_CODE = "[012]"


class FiberLogReader(object):
    def __init__(self, log: Path):
        with log.open("r") as f:
            loglines = f.readlines()

        areas = {"timestamp": [], "area": []}
        recordings = {"timestamp": [], "record_number": []}
        events = {
            "door_open": {},
            "animal_out": {},
        }
        record_number = None
        for line in loglines:
            area_parse = parse_area_from_logline(line)
            if area_parse:
                timestamp, area = area_parse
                areas["area"].append(area)
                areas["timestamp"].append(timestamp)
                continue

            record_parse = parse_mousename_record_from_logline(line)
            if record_parse:
                timestamp, mouse_name, record_number = record_parse
                recordings["record_number"].append(record_number)
                recordings["timestamp"].append(timestamp)
                continue

            if DOOR_OPEN_CODE in line and record_number:
                timestamp = parse_timestamp_from_logline(line)
                if timestamp and record_number not in events["door_open"]:
                    events["door_open"][record_number] = timestamp
                continue

            if ANIMAL_OUT_CODE in line and record_number:
                timestamp = parse_timestamp_from_logline(line)
                if timestamp and record_number not in events["animal_out"]:
                    events["animal_out"][record_number] = timestamp
                continue

        self.areas = {
            "timestamp": np.array(areas["timestamp"], dtype="datetime64[us]"),
            "area": np.array(areas["area"]),
        }
        self.recordings = {
            "timestamp": np.array(recordings["timestamp"], dtype="datetime64[us]"),
            "record_number": np.array(recordings["record_number"]),
        }

        self.events = events

    def areas_from_timestamps(self, timestamps: pd.Series):
        query = timestamps.astype("datetime64[us]").to_numpy()
        # searchsorted returns indices such that if element were to be
        # inserted at those idx, the array would be sorted
        # We actually want the timestamp BEFORE the ones requested to know
        # where we are at the timestamp
        idx = np.searchsorted(self.areas["timestamp"], query, side="left") - 1
        return self.areas["area"][idx]

    def recordings_start(self) -> datetime:
        return self.recordings["timestamp"][0]

    def recording_start(self, recording: int) -> datetime:
        index = np.where(self.recordings["record_number"] == recording)[0][0]
        return self.recordings["timestamp"][index]


def parse_timestamp_from_logline(line: str) -> datetime | None:
    # "2026-04-27 16:41:09.623"
    match = re.match(r"(\d+-\d+-\d+\s\d+:\d+:\d+\.\d+):", line)
    if match:
        time = match.group(1)
        date = datetime.fromisoformat(time)
        return date
    return None


def parse_mousename_record_from_logline(line: str):
    # RWD mode example:
    # 2026-04-27 16:41:09.877: photometry control: starting with filename: Sh2Het86SSfiber270426 1
    # PYPHOTOMETRY mode example:
    # 2026-01-23 15:21:43.051: starting photometry record Sh2WT87SS1b 2
    record_re = re.compile(
        r"(?:photometry control: starting with filename:|starting photometry record)"
        r"\s*(?P<mouse_name>\w+)\s+(?P<record_number>\d+)"
    )
    record_match = record_re.search(line)
    if not record_match:
        return None

    record_number = int(record_match["record_number"])
    mouse_name = record_match["mouse_name"]
    timestamp = parse_timestamp_from_logline(line)
    if not timestamp:
        logger.warning(f"Couldn't parse timestamp: {line}")

    return timestamp, mouse_name, record_number


def parse_area_from_logline(line: str):
    # Turret set position to : SOCIAL_BOX
    area = None
    area_re = re.compile(r"Turret set position to :\s*(?P<area>\w+)")
    area_match = area_re.search(line)
    if area_match:
        area = area_match["area"]
    else:
        return None

    timestamp = parse_timestamp_from_logline(line)
    if not timestamp:
        logger.warning(f"Couldn't parse timestamp: {line}")
    return timestamp, area


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log87 = Path.cwd().joinpath("data/autres_manip/Manip_souris87/fullLog.txt")
    t = datetime.fromisoformat("2026-01-23 15:25:48.812")
    log_reader = FiberLogReader(log87)
    area = log_reader.areas_from_timestamps(pd.Series([t]))

    logger.debug(area)
    logger.debug(log_reader.events["door_open"].__len__())
    logger.debug(log_reader.events["door_open"].__len__())
    logger.debug(log_reader.events["door_open"].keys())
    logger.debug(log_reader.events["door_open"][6])

    if False:  # log parsing
        log87 = Path.cwd().joinpath("data/autres_manip/Manip_souris87/fullLog.txt")
        log83 = Path.cwd().joinpath(
            "data/autres_manip/Manip_souris83/testLog - 2026-04-27Sh2Het83SSFiber.log.txt"
        )
        area83, recordings83 = FiberLogReader(log83)
        area87, recordings87 = FiberLogReader(log87)
        print(area87.keys())
        breakpoint()
