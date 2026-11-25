import logging
from datetime import timedelta
from pathlib import Path

from plotly import graph_objects as go

from src.lib.fiber_data_format import FiberAcquisitionMode
from src.lib.FiberLogReader import FiberLogReader
from src.lib.processing import area_under_curve, get_baseline
from src.lib.recordings import (
    find_log_from_mouse_folder,
    get_fullname_component_from_fullpath,
    parse_name_number_from_path,
    parse_recording,
    recording_has_events,
)
from src.utils import setup_logging

logger = logging.getLogger(__name__)


def auc_plot(
    recording_path: Path,
    mouse_folder: Path,
    mode: FiberAcquisitionMode,
    baseline_delta=timedelta(seconds=1.0),
    after_out_door_delta=timedelta(seconds=25.0),
):

    # Get log from glob mouse folder
    log = find_log_from_mouse_folder(mouse_folder)
    log_reader = FiberLogReader(log)

    # Validate recording
    name_number = parse_name_number_from_path(recording_path, mode)
    if name_number:
        _, recording_number = name_number
    else:
        error_message = f"Could not parse recording number: {recording_path}"
        logger.debug(error_message)
        return None, error_message
    valid = recording_has_events(recording_number, log_reader)
    if not valid:
        error_message = f"Recording has no parsed events: {recording_path}"
        logger.debug(error_message)
        return None, error_message

    # Get recording as DataFrame
    df = parse_recording(recording_path, mode, log_reader)

    baseline_time, baseline = get_baseline(
        df, log_reader, recording_number, baseline_delta
    )

    df, auc_between, auc_after = area_under_curve(
        df, log_reader, recording_number, baseline_delta, after_out_door_delta
    )

    fig = go.Figure()
    time_series_s = df["TimeStamp"].dt.total_seconds()
    fig.add_trace(go.Scatter(x=time_series_s, y=df["delta_f"], name="Delta f"))

    # Baseline horizontal line
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
    return fig, None


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
