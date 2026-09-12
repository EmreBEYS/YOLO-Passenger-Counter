from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """YOLO Passenger Counter application settings."""

    BASE_DIR: Path = Path(__file__).resolve().parent

    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOG_DIR / "passenger_log.csv"

    MODEL_PATH: Path = BASE_DIR / "yolov8s.pt"
    PERSON_CLASS_ID: int = 0

    # Sensitive settings for crowded, partially occluded bus interiors.
    CONFIDENCE_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.45
    INFERENCE_SIZE: int = 960
    MAX_DETECTIONS: int = 100

    DISPLAY_WIDTH: int = 960
    DISPLAY_HEIGHT: int = 540

    FRAME_SKIP: int = 1
    LOG_EVERY_N_FRAMES: int = 10