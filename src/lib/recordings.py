import logging
import re
from pathlib import Path

import pandas as pd

from src.lib.fiber_data_format import FiberAcquisitionMode
from src.lib.FiberLogReader import FiberLogReader
from src.lib.processing import delta_f
from src.utils import setup_logging

RecordingNumber = int

logger = logging.getLogger(__name__)


def get_fullname_component_from_fullpath(path: Path, mode: FiberAcquisitionMode) -> str:
    match mode:
        case FiberAcquisitionMode.RWD:
            name = path.parent.parent.name
            return name
        case FiberAcquisitionMode.PYPHOTOMETRY:
            name = path.stem
            return name


def parse_name_number_from_full(fullname: str) -> tuple[str, RecordingNumber] | None:
    match = re.match(r"(\w+)\s+(\d+)", fullname)
    if match:
        name, number = match.groups()
        return name, int(number)
    return None


def find_log_from_mouse_folder(mouse_folder: Path):
    log_match = list(mouse_folder.glob("*.txt"))
    if len(log_match) > 1:
        raise ValueError("Too many txt found, expect only 1")
    if len(log_match) == 0:
        raise ValueError("No log found")

    return log_match[0]


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
    recordings: list[tuple[RecordingNumber, str, Path]],
    log_reader: FiberLogReader,
) -> pd.DataFrame:
    """
    Aggregate all samples froma all recordings into a single DataFrame. Use the
    log file to get the area

    """

    dfs = []
    latest_timestamp = 0
    for record_number, _, record_path in recordings:
        record_df = pd.read_csv(record_path, skiprows=1)
        record_df = record_df.loc[:, ~record_df.columns.str.contains("^Unnamed")]
        if "Events" in record_df.columns:
            del record_df["Events"]

        record_df["TimeStamp"] += latest_timestamp
        record_df["record_number"] = record_number
        # Each recording start their timestamp at 0, offset each recording
        # TODO: recording are not consecutive, should use the log to know the actual recording
        # start instead
        latest_timestamp = max(record_df["TimeStamp"])
        dfs.append(record_df)

    df = pd.concat(dfs)
    ch410 = df.iloc[:, 1]
    ch470 = df.iloc[:, 2]
    df["delta_f"] = delta_f(ch410, ch470)
    start = log_reader.recordings_start()  # Timestamp of the start of the 1st recording
    actual_timestamps = start + pd.to_timedelta(df["TimeStamp"], unit="ms")
    df["area"] = log_reader.areas_from_timestamps(actual_timestamps)
    return df


if __name__ == "__main__":
    setup_logging(debug=True)
    pyphotometry_path = Path("data/autres_manip/Manip_souris87/Sh2WT87SS1b 10.csv")
    rwd_path = Path.cwd().joinpath(
        "data/autres_manip/Manip_souris83/Sh2Het86SSfiber270426 1/2026_04_27-16_41_10/Fluorescence.csv"
    )
    pyphotometry = get_fullname_component_from_fullpath(
        pyphotometry_path, FiberAcquisitionMode.PYPHOTOMETRY
    )
    print(pyphotometry)
    rwd = get_fullname_component_from_fullpath(rwd_path, FiberAcquisitionMode.RWD)
    print(rwd)

    print(parse_name_number_from_full(rwd), parse_name_number_from_full(pyphotometry))
