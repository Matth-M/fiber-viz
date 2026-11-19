import logging
from datetime import datetime
from pathlib import Path


def datetime_to_str(d: datetime) -> str:
    date_format = "%FT%H%M%S"
    return d.now().strftime(date_format)


def get_time() -> str:
    return datetime_to_str(datetime.now())


project_root = Path(__file__).parent.parent
DATA_ROOT = project_root.joinpath("data")


def setup_logging(debug: bool):
    # Logging
    logDir = Path.cwd().joinpath(".logs")
    logDir.mkdir(exist_ok=True)
    logFile = logDir.joinpath(f"{get_time()}.log")

    # TODO:
    # Symlink can cause OSError
    # symlink = logFile.parent.joinpath("latest.log")
    # if symlink.exists():
    #     symlink.unlink()
    # symlink.symlink_to(logFile)

    fileLogs = logging.FileHandler(logFile)
    streamLog = logging.StreamHandler()

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        handlers=[fileLogs, streamLog],
        format="%(levelname)s:%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s",
    )
