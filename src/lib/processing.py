import logging
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.lib.fiber_data_format import FiberAcquisitionMode
from src.lib.FiberLogReader import FiberLogReader
from src.lib.recordings import RecordingId, parse_recording
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
    baseline_delta=timedelta(seconds=1.0),
    after_out_door_delta=timedelta(seconds=25.0),
    dx=0.02,  # 1 sample every 0.02 second
):

    df["delta_f"] = delta_f(df["CH1-410"], df["CH1-470"])

    # Baseline
    _, baseline_value = get_baseline(df, log_reader, recording_number, baseline_delta)
    df["delta_f_baseline"] = df["delta_f"] - baseline_value
    df["delta_f_baseline_clipped"] = df["delta_f_baseline"].clip(lower=0)

    # AUC between door_open and animal_out events
    door_open_datetime = log_reader.events["door_open"][recording_number]
    animal_out_datetime = log_reader.events["animal_out"][recording_number]
    df_between_events = df[df["date"].between(door_open_datetime, animal_out_datetime)]
    auc_between = np.trapezoid(df_between_events["delta_f_baseline"], dx=dx)
    between_events_duration = (animal_out_datetime - door_open_datetime).total_seconds()
    normalized_auc_between = auc_between / between_events_duration

    # AUC  animal_out after event
    df_after = df[
        df["date"].between(
            animal_out_datetime, animal_out_datetime + after_out_door_delta
        )
    ]
    auc_after = np.trapezoid(df_after["delta_f_baseline"], dx=dx)
    after_duration = (
        animal_out_datetime - animal_out_datetime + after_out_door_delta
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
