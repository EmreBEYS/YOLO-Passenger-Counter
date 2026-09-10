import csv
from datetime import datetime
from pathlib import Path

from config import AppConfig
from passenger_counter.counter import CounterResult


class EventLogger:
    """
    Yolcu sayım sonuçlarını CSV dosyasına yazar.
    """

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()
        self.log_file: Path = self.config.LOG_FILE

        self.config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_header()

    def _ensure_header(self) -> None:
        """
        CSV dosyası yoksa başlık satırını oluşturur.
        """
        if self.log_file.exists():
            return

        with self.log_file.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "timestamp",
                    "source",
                    "entered",
                    "exited",
                    "inside",
                    "detected_count",
                ]
            )

    def write(self, source: str, result: CounterResult) -> None:
        """
        Tek bir sayım sonucunu CSV dosyasına yazar.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.log_file.open("a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    timestamp,
                    source,
                    result.entered,
                    result.exited,
                    result.inside,
                    result.detected_count,
                ]
            )