import argparse
import io
import logging
import re
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

SAMPLE_RATE = 100
SCALE_ANALOG_VALUE = 1 / 100


class FiberAcquisitionMode(Enum):
    PYPHOTOMETRY = "PYPHOTOMETRY"
    RWD = "RWD"


def parse_recording(filepath: Path, mode: FiberAcquisitionMode) -> pd.DataFrame:
    match mode:
        case FiberAcquisitionMode.PYPHOTOMETRY:
            return parse_pyphotometry_csv(filepath)
        case FiberAcquisitionMode.RWD:
            return parse_rwd_csv(filepath)


def parse_rwd_csv(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(
        filepath,
        skiprows=1,
        index_col=False,
    )
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df


def parse_pyphotometry_csv(
    filepath: Path,
    sample_rate=SAMPLE_RATE,
    scale=SCALE_ANALOG_VALUE,
) -> pd.DataFrame:
    with filepath.open("r") as f:
        raw_content = f.readlines()
        # 1st line is json metadata
        # this data is malformed, don't read it
        content = raw_content[1:]

    # Remove timestamp and events lines in the csv
    # Use the first timestamp line to get the start of recording
    # Store events with the timestamps, the re add a column events
    # with events inserted at the right time from their absolute timestamp
    # and the start timestamp
    cleaned_content: list[str] = []
    events = []
    first_timestamp_read = False
    start = None
    for line in content:
        if line.startswith("timestamp") and not first_timestamp_read:
            first_timestamp_read = True
            start_str = line.strip().split(",")[-1]
            start = datetime.fromisoformat(start_str)

        if line.startswith("ExternalEvent"):
            # event line example:
            # ExternalEvent,poke sugar ok,2026-10-26 17:32:33.997770
            logger.debug(line)
            _, event, timestamp = line.strip().split(",")
            evt_timestamp = datetime.fromisoformat(timestamp)
            events.append((event, evt_timestamp))

        if not line.startswith(("timestamp", "ExternalEvent")):
            cleaned_content.append(line.strip())

    df = pd.read_csv(
        io.StringIO("\n".join(cleaned_content)),
        index_col=False,  # There is no index column in the csv file
        dtype=np.float64,
    )
    df = df.loc[:, ~df.columns.str.contains("^Unnamed|Digital")]

    event_column = [""] * len(df)
    sample_rate_us = sample_rate / 10**6
    for text, timestamp in events:
        delta_us = (timestamp - start).microseconds
        event_idx = round(delta_us * sample_rate_us)
        event_column[event_idx] = text

    # RWD columns:
    # TimeStamp, Events, CH1-410, CH1-470
    df["Events"] = event_column
    for col in df.columns:
        if re.search("Analog", col):
            df[col] *= scale

    return df


def convert_RWD_and_write(csv_path: Path, out_directory: Path):
    df = parse_pyphotometry_csv(csv_path)
    write_RWD_csv(df, csv_path.stem, out_directory)


def read_header() -> str:
    with Path("./data/rwd_header.txt").open("r") as f:
        return f.read()


def write_RWD_csv(df: pd.DataFrame, name: str, out_directory: Path):
    header = read_header()
    out_directory.mkdir(exist_ok=True)
    output_path = out_directory.joinpath(Path(f"RWD_{name}.csv"))
    with output_path.open("w", encoding="utf-8") as f:
        # RWD requires a header to read data files
        f.write(header)
        df.write_csv(f)


def convert_directory_RWD(input_dir: Path, out_directory: Path, write=True):
    data_files = list(input_dir.glob("*.csv"))
    with ProcessPoolExecutor(max_workers=16) as executor:
        executor.map(
            convert_RWD_and_write,
            data_files,
            [out_directory] * len(data_files),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        help="directory containing the input files (CSV)",
    )
    parser.add_argument("--debug", "-d", action="store_true")
    parser.add_argument("--dry-run", "-n", action="store_true")

    args = parser.parse_args()

    loglevel = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=loglevel)

    if True:  # 2 files test
        filepath1 = Path(
            "./data/SSFibermaleSh2KO28_26_10_26 social Phase.PHASE2 68_0-2026-10-26-183204.csv"
        )
        filepath2 = Path(
            "./data/TestSh2WT88 social Phase.PHASE1 12_0-2026-10-01-171527.csv"
        )
        f = Path(
            "../Sh2KO28_26_10_26/SSFibermaleSh2KO28_26_10_26 sugar Phase.PHASE2 74_0-2026-10-26-202148.csv"
        )

        df = parse_pyphotometry_csv(f)
        df1 = parse_pyphotometry_csv(filepath1)
        df2 = parse_pyphotometry_csv(filepath2)

        out_dir = Path("out")
        write = not args.dry_run
        if write:
            write_RWD_csv(df1, filepath1.stem, out_dir)
            write_RWD_csv(df2, filepath2.stem, out_dir)
    if False:
        input_dir = args.directory
        now = datetime.now()
        now_str = now.strftime("%Y%m%dT%H%M%S")
        write = not args.dry_run
        output_directory = Path(f"out_{input_dir.stem}_{now_str}")
        if write:
            output_directory.mkdir()
        convert_directory_RWD(input_dir, output_directory, write)
