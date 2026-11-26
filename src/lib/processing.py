import logging
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.lib.constants import DEFAULT_AFTER_OUT_DELTA, DEFAULT_BASELINE_DELTA
from src.lib.fiber_data_format import FiberAcquisitionMode
from src.lib.FiberLogReader import FiberLogReader
from src.lib.recordings import (
    RecordingId,
    find_log_from_mouse_folder,
    get_recordings_mouse_folder,
    parse_recording,
    validate_recording,
)
from src.utils import setup_logging

logger = logging.getLogger(__name__)


def mouse_export_auc_data(
    mouse_folder: Path,
    mode: FiberAcquisitionMode,
    baseline_delta=DEFAULT_BASELINE_DELTA,
    after_out_door_delta=DEFAULT_AFTER_OUT_DELTA,
) -> pd.DataFrame:
    data = {"recording_number": [], "auc_between": [], "auc_after_door_exit": []}
    log_reader = FiberLogReader(find_log_from_mouse_folder(mouse_folder))
    for recording_number, _, recording_path in get_recordings_mouse_folder(
        mouse_folder, mode
    ):
        _, auc_between, auc_after, err_msg = auc_data(
            recording_path, mode, log_reader, baseline_delta, after_out_door_delta
        )
        if err_msg:
            logger.warning(err_msg)
            continue

        data["recording_number"].append(recording_number)
        data["auc_between"].append(auc_between)
        data["auc_after_door_exit"].append(auc_after)

    return pd.DataFrame(data)


def auc_data(
    recording_path: Path,
    mode: FiberAcquisitionMode,
    log_reader: FiberLogReader,
    baseline_delta=DEFAULT_BASELINE_DELTA,
    after_out_door_delta=DEFAULT_AFTER_OUT_DELTA,
):
    _, recording_number, err_msg = validate_recording(
        recording_path,
        log_reader,
        mode,
    )
    if err_msg:
        return None, None, None, err_msg

    # Get recording as DataFrame
    df = parse_recording(recording_path, mode, log_reader)
    if df is None:
        return None, None, None, err_msg

    baseline_opt = get_baseline(df, log_reader, recording_number, baseline_delta)
    if baseline_opt:
        baseline_time, baseline = baseline_opt
    else:
        return None, None, None, "Could not get baseline"

    df, auc_between, auc_after = area_under_curve(
        df, log_reader, recording_number, baseline_delta, after_out_door_delta
    )

    return df, auc_between, auc_after, None


def delta_f(ch410, ch470):
    fit_coeffs = np.polyfit(ch410, ch470, 1)
    isofit = np.polyval(fit_coeffs, ch410)
    return ((ch470 - isofit) / isofit) * 100


def get_baseline_date(
    recording_number: RecordingId,
    log_reader: FiberLogReader,
    baseline_delta=DEFAULT_BASELINE_DELTA,
) -> datetime:
    door_open_datetime = log_reader.events["door_open"][recording_number]
    return door_open_datetime - baseline_delta


def get_baseline(
    df: pd.DataFrame,
    log_reader: FiberLogReader,
    recording_number: RecordingId,
    baseline_delta=timedelta(seconds=1.0),
) -> tuple[datetime, float] | None:
    # Baseline
    baseline_datetime = get_baseline_date(recording_number, log_reader, baseline_delta)
    if "delta_f" not in df:
        df["delta_f"] = delta_f(df["CH1-410"], df["CH1-470"])

    after_baseline_time_df = df[df["date"] >= baseline_datetime]
    if len(after_baseline_time_df) == 0:
        logger.debug(f"No samples after baseline: {recording_number}")
        return None

    baseline_value = after_baseline_time_df.iloc[0]["delta_f"]

    return baseline_datetime, baseline_value


def area_under_curve(
    df: pd.DataFrame,
    log_reader: FiberLogReader,
    recording_number: int,
    baseline_delta=DEFAULT_BASELINE_DELTA,
    after_out_door_delta=DEFAULT_AFTER_OUT_DELTA,
    dx=0.02,  # 1 sample every 0.02 second
):

    df["delta_f"] = delta_f(df["CH1-410"], df["CH1-470"])

    # Baseline
    baseline_opt = get_baseline(df, log_reader, recording_number, baseline_delta)
    if baseline_opt:
        _, baseline_value = baseline_opt
    else:
        return None
    df["delta_f_baseline"] = df["delta_f"] - baseline_value
    df["delta_f_baseline_clipped"] = df["delta_f_baseline"].clip(lower=0)

    # AUC between door_open and animal_out events
    door_open_datetime = log_reader.events["door_open"][recording_number]
    animal_out_datetime = log_reader.events["animal_out"][recording_number]
    df_between_events = df[df["date"].between(door_open_datetime, animal_out_datetime)]
    auc_between = np.trapezoid(df_between_events["delta_f_baseline_clipped"], dx=dx)
    between_events_duration = (animal_out_datetime - door_open_datetime).total_seconds()
    normalized_auc_between = auc_between / between_events_duration

    # AUC  animal_out after event
    df_after = df[
        df["date"].between(
            animal_out_datetime, animal_out_datetime + after_out_door_delta
        )
    ]
    auc_after = np.trapezoid(df_after["delta_f_baseline_clipped"], dx=dx)
    after_duration = (
        animal_out_datetime - animal_out_datetime + after_out_door_delta
    ).total_seconds()
    normalized_auc_after = auc_after / after_duration

    return df, normalized_auc_between, normalized_auc_after


if __name__ == "__main__":
    setup_logging(debug=True)

    if False:
        log = Path.cwd().joinpath(
            "data/autres_manip/Manip_souris83/testLog - 2026-04-27Sh2Het83SSFiber.log.txt"
        )
        recording_csv = Path.cwd().joinpath(
            "./data/autres_manip/Manip_souris83/Sh2Het86SSfiber270426 9/2026_04_27-16_50_59/Fluorescence.csv"
        )
        recording = 9

        log_reader = FiberLogReader(log)
        df = parse_recording(recording_csv, FiberAcquisitionMode.RWD)
        be, af = area_under_curve(df, log_reader, recording)

    if True:
        mouse_folder = Path.cwd().joinpath("./data/autres_manip/Manip_souris83")
        mouse_folder = Path.cwd().joinpath("./data/autres_manip/Manip_souris87")
        df = mouse_export_auc_data(
            mouse_folder,
            FiberAcquisitionMode.PYPHOTOMETRY,
        )
        print(df)
