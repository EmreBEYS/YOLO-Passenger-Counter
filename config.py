from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """
    YOLO Passenger Counter genel ayarları.
    """

    # Proje kök dizini
    BASE_DIR: Path = Path(__file__).resolve().parent

    # Veri klasörleri
    DATA_DIR: Path = BASE_DIR / "data"
    PRIVATE_DATA_DIR: Path = DATA_DIR / "private"
    PRIVATE_VIDEO_DIR: Path = PRIVATE_DATA_DIR / "videos"
    PRIVATE_IMAGE_DIR: Path = PRIVATE_DATA_DIR / "images"

    # Log klasörü ve dosyası
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOG_DIR / "passenger_log.csv"

    # YOLO ayarları
    MODEL_NAME: str = "yolov8n.pt"
    PERSON_CLASS_ID: int = 0
    CONFIDENCE_THRESHOLD: float = 0.35

    # Görüntü ayarları
    DISPLAY_WIDTH: int = 960
    DISPLAY_HEIGHT: int = 540

    # Video işleme
    FRAME_SKIP: int = 1