import logging
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.lib.fiber_data_format import parse_rwd_csv
from src.lib.FiberLogReader import FiberLogReader
from src.utils import setup_logging

logger = logging.getLogger(__name__)


def delta_f(ch410, ch470):
    fit_coeffs = np.polyfit(ch410, ch470, 1)
    isofit = np.polyval(fit_coeffs, ch410)
    return ((ch470 - isofit) / isofit) * 100


def get_baseline_time(
    recording_number: RecordingId,
    log_reader: FiberLogReader,
    baseline_delta=timedelta(seconds=1.0),
) -> datetime:
    door_open_datetime = log_reader.events["door_open"][recording_number]
    return door_open_datetime - baseline_delta


def get_baseline(
    df: pd.DataFrame,
    log_reader: FiberLogReader,
    recording_number: RecordingId,
    baseline_delta=timedelta(seconds=1.0),
) -> tuple[datetime, float]:
    # Baseline
    baseline_datetime = get_baseline_time(recording_number, log_reader, baseline_delta)
    if "delta_f" not in df:
        df["delta_f"] = delta_f(df["CH1-410"], df["CH1-470"])

    baseline_value = df[df["date"] >= baseline_datetime].iloc[0]["delta_f"]
    return baseline_datetime, baseline_value



def area_under_curve(
    df: pd.DataFrame,
    log_reader: FiberLogReader,
    recording_number: int,
    baseline_delta_ms: int = 1000,
    after_out_door_delta_s=25,
    dx: float = 0.02,  # 1 sample every 0.02 second
):

    recording_start = log_reader.recording_start(recording_number)
    df["TimeStamp"] = pd.to_datetime(
        df["TimeStamp"],
        unit="ms",
        origin=recording_start,
    )
    df["delta_f"] = delta_f(df["CH1-410"], df["CH1-470"])

    baseline_delta = timedelta(seconds=baseline_delta_ms)
    door_open_timestamp = log_reader.events["door_open"][recording_number]
    baseline_timestamp = door_open_timestamp - baseline_delta
    baseline_value = df[df["TimeStamp"] >= baseline_timestamp].iloc[0]["delta_f"]
    df["delta_f_baseline"] = (df["delta_f"] - baseline_value).clip(lower=0)

    animal_out_timestamp = log_reader.events["animal_out"][recording_number]
    df_between_events = df[
        df["TimeStamp"].between(door_open_timestamp, animal_out_timestamp)
    ]
    auc_between = np.trapezoid(df_between_events["delta_f_baseline"], dx=dx)
    between_events_duration = (
        animal_out_timestamp - door_open_timestamp
    ).total_seconds()
    normalized_auc_between = auc_between / between_events_duration

    delta_after = timedelta(seconds=after_out_door_delta_s)
    df_after = df[
        df["TimeStamp"].between(
            animal_out_timestamp, animal_out_timestamp + delta_after
        )
    ]
    auc_after = np.trapezoid(df_after["delta_f_baseline"], dx=dx)
    after_duration = (
        animal_out_timestamp - animal_out_timestamp + delta_after
    ).total_seconds()
    normalized_auc_after = auc_after / after_duration

    return df, normalized_auc_between, normalized_auc_after


if __name__ == "__main__":
    setup_logging(debug=True)
    log = Path.cwd().joinpath(
        "data/autres_manip/Manip_souris83/testLog - 2026-04-27Sh2Het83SSFiber.log.txt"
    )
    recording_csv = Path.cwd().joinpath(
        "./data/autres_manip/Manip_souris83/Sh2Het86SSfiber270426 9/2026_04_27-16_50_59/Fluorescence.csv"
    )
    recording = 9

    log_reader = FiberLogReader(log)
    df = parse_rwd_csv(recording_csv)
    be, af = area_under_curve(df, log_reader, recording)
