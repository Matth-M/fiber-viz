import logging
from pathlib import Path

from plotly import graph_objects as go

from src.lib.constants import DEFAULT_AFTER_OUT_DELTA, DEFAULT_BASELINE_DELTA
from src.lib.fiber_data_format import FiberAcquisitionMode
from src.lib.FiberLogReader import FiberLogReader
from src.lib.processing import auc_data, get_baseline
from src.lib.recordings import (
    find_log_from_mouse_folder,
    validate_recording,
)
from src.utils import setup_logging

logger = logging.getLogger(__name__)


def auc_plot(
    recording_path: Path,
    mouse_folder: Path,
    mode: FiberAcquisitionMode,
    baseline_delta=DEFAULT_BASELINE_DELTA,
    after_out_door_delta=DEFAULT_AFTER_OUT_DELTA,
):
    # Get log from glob mouse folder
    log = find_log_from_mouse_folder(mouse_folder)
    log_reader = FiberLogReader(log)

    _, recording_number, err_msg = validate_recording(recording_path, log_reader, mode)
    if err_msg:
        logger.debug(err_msg)
        return None, None, None, err_msg

    df, auc_between, auc_after, err_msg = auc_data(
        recording_path, mode, log_reader, baseline_delta, after_out_door_delta
    )
    if err_msg:
        logger.debug(err_msg)
        return None, None, None, err_msg

    fig = go.Figure()
    time_series_s = df["TimeStamp"].dt.total_seconds()
    fig.add_trace(go.Scatter(x=time_series_s, y=df["delta_f"], name="Delta f"))

    # Baseline horizontal line
    baseline_time, baseline = get_baseline(
        df, log_reader, recording_number, baseline_delta
    )
    time_baseline_s = df[df["date"] >= baseline_time]["TimeStamp"].dt.total_seconds()
    baseline_y = [baseline] * (len(time_baseline_s))
    fig.add_trace(
        go.Scatter(
            x=time_baseline_s,
            y=baseline_y,
            line={"dash": "dash", "color": "grey"},
            name="baseline",
        )
    )

    recording_start = log_reader.recording_start(recording_number)

    # Door open
    door_open_event_datetime = log_reader.events["door_open"][recording_number]
    door_open_x = (door_open_event_datetime - recording_start).total_seconds()
    fig.add_vline(
        x=door_open_x,
        line_width=3,
        line_dash="dash",
        line_color="green",
        annotation_text="door_open",
    )

    # Animal out
    animal_out_event_datetime = log_reader.events["animal_out"][recording_number]
    animal_out_x = (animal_out_event_datetime - recording_start).total_seconds()
    fig.add_vline(
        x=animal_out_x,
        line_width=3,
        line_dash="dash",
        line_color="red",
        annotation_text="animal_out",
    )

    # After out end
    after_out_x = (
        animal_out_event_datetime + after_out_door_delta - recording_start
    ).total_seconds()
    fig.add_vline(
        x=after_out_x,
        line_width=3,
        line_dash="dash",
        line_color="brown",
        annotation_text=f"animal_out + {after_out_door_delta.total_seconds()}s",
    )

    fig.update_layout(
        title="Area under curve Delta f",
        xaxis_title="Time (s)",
        yaxis_title="Deltaf",
    )
    return fig, auc_between, auc_after, None


if __name__ == "__main__":
    setup_logging(debug=True)

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--show", "-s", action="store_true")
    args = parser.parse_args()

    if True:
        mouse_folder = Path.cwd().joinpath("data/autres_manip/Manip_souris83")

        recording1 = mouse_folder.joinpath(
            "Sh2Het86SSfiber270426 1/2026_04_27-16_41_10/Fluorescence.csv"
        )
        recording209 = mouse_folder.joinpath(
            "Sh2Het86SSfiber270426 209/2026_04_29-03_00_00/Fluorescence.csv"
        )

        recording167 = mouse_folder.joinpath(
            "Sh2Het86SSfiber270426 167/2026_04_28-19_00_00/Fluorescence.csv"
        )

        recording = Path.cwd().joinpath(
            "data/autres_manip/Manip_souris88/Sh2wt88SSfiber040526 94/2026_05_05-07_22_38/Fluorescence.csv"
        )

        mode = FiberAcquisitionMode.RWD

        fig = auc_plot(recording, mouse_folder, mode)

        if args.show:
            if fig:
                fig.show()
