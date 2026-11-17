import logging
from pathlib import Path

import pandas as pd

from src.lib.fiber_data_format import FiberAcquisitionMode
from src.lib.FiberLogReader import FiberLogReader
from src.lib.processing import delta_f

RecordingNumber = int

logger = logging.getLogger(__name__)


def parse_mouse_recording_name(filename: str) -> tuple[int, str]:
    name, record_number = filename.split(maxsplit=1)
    return (int(record_number), name)


def get_recordings_mouse_folder(
    mouse_folder: Path, mode: FiberAcquisitionMode
) -> list[tuple[RecordingNumber, str, Path]]:
    recordings = []
    match mode:
        case FiberAcquisitionMode.PYPHOTOMETRY:
            # Every recording are in same folder, name gives information on record number and
            # mouse name
            for f in mouse_folder.glob("*.csv"):
                filename = f.stem
                try:
                    recording_number, recording_name = parse_mouse_recording_name(
                        filename
                    )
                    recordings.append((recording_number, recording_name, f))
                except ValueError:
                    # Malformed filename with recording_number == '10kk'
                    # is it 10, 100, 1000 ? Skip it
                    logger.debug(f"unexpected filename format: {f}")
                    continue
        case FiberAcquisitionMode.RWD:
            # Each recording is in a separate directory, wich contains a timestamp folder,
            # then all the csv. The fiber samples are in Fluorescence.csv
            for f in mouse_folder.glob("**/Fluorescence.csv"):
                recording_folder_name = f.parent.parent.name
                (
                    recording_number,
                    recording_name,
                ) = parse_mouse_recording_name(recording_folder_name)
                recordings.append((recording_number, recording_name, f))
    # Sort by recording number
    return sorted(recordings, key=lambda x: x[0])


def parse_samples_from_recordings(
    recordings: list[tuple[RecordingNumber, Path]],
    log_reader: FiberLogReader,
) -> pd.DataFrame:

    dfs = []
    latest_timestamp = 0
    for record_number, record_path in recordings:
        record_df = pd.read_csv(record_path, skiprows=1)
        record_df = record_df.loc[:, ~record_df.columns.str.contains("^Unnamed")]
        if "Events" in record_df.columns:
            del record_df["Events"]

        record_df["TimeStamp"] += latest_timestamp
        record_df["record_number"] = record_number
        latest_timestamp = max(record_df["TimeStamp"])
        dfs.append(record_df)

    df = pd.concat(dfs)
    ch410 = df.iloc[:, 1]
    ch470 = df.iloc[:, 2]
    df["delta_f"] = delta_f(ch410, ch470)
    start = log_reader.recording_start()
    actual_timestamps = start + pd.to_timedelta(df["TimeStamp"], unit="ms")
    df["area"] = log_reader.areas_from_timestamps(actual_timestamps)
    return df
