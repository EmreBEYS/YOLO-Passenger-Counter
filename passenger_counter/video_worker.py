import time
from pathlib import Path
from typing import Callable, Optional

import cv2

from config import AppConfig
from passenger_counter.counter import PassengerCounter, CounterResult
from passenger_counter.detector import PassengerDetector
from passenger_counter.event_logger import EventLogger


FrameCallback = Callable[[object, CounterResult], None]
StatusCallback = Callable[[str], None]


class VideoWorker:
    """
    Video/kamera akışını işler.

    Görevleri:
    - Kamera veya video dosyası açar
    - Frame okur
    - YOLO ile kişi tespiti yapar
    - Counter ile sayım üretir
    - Logger ile CSV kaydı atar
    - UI tarafına görüntü ve sayım sonucunu yollar
    """

    def __init__(
        self,
        source: int | str | Path,
        frame_callback: FrameCallback,
        status_callback: Optional[StatusCallback] = None,
        config: AppConfig | None = None,
    ) -> None:
        self.source = source
        self.frame_callback = frame_callback
        self.status_callback = status_callback
        self.config = config or AppConfig()

        self.detector: PassengerDetector
        self.counter: PassengerCounter
        self.logger: EventLogger

        self.running = False
        self.stop_requested = False
        self.frame_index = 0

    def start(self) -> None:
        """Run video analysis. This method should execute in a worker thread."""
        capture = None
        try:
            self._send_status("Loading YOLO model...")
            self.detector = PassengerDetector(self.config)
            self.counter = PassengerCounter()
            self.logger = EventLogger(self.config)

            if self.stop_requested:
                self._send_status("Analysis cancelled")
                return

            self.running = True
            self._send_status("Analysis started")
            capture = cv2.VideoCapture(
                str(self.source) if not isinstance(self.source, int) else self.source
            )

            if not capture.isOpened():
                self._send_status(f"Unable to open source: {self.source}")
                return

            source_name = self._get_source_name()

            while self.running:
                success, frame = capture.read()
                if not success:
                    self._send_status("Video ended or the next frame could not be read")
                    break

                self.frame_index += 1
                if (
                    self.config.FRAME_SKIP > 1
                    and self.frame_index % self.config.FRAME_SKIP != 0
                ):
                    continue

                detections = self.detector.detect(frame)
                result = self.counter.update(detections)
                annotated_frame = self.detector.draw_detections(frame, detections)
                self._draw_counter_info(annotated_frame, result)

                if self.frame_index % self.config.LOG_EVERY_N_FRAMES == 0:
                    self.logger.write(source_name, result)

                print(
                    f"Frame: {self.frame_index} | "
                    f"Passenger Count: {result.detected_count} | "
                    f"Status: {result.density_status}"
                )
                self.frame_callback(annotated_frame, result)
                time.sleep(0.001)
        except Exception as error:
            self._send_status(f"Analysis error: {error}")
        finally:
            if capture is not None:
                capture.release()
            self.running = False
            self._send_status("Analysis stopped")

    def stop(self) -> None:
        """
        Video işleme döngüsünü durdurur.
        """
        self.stop_requested = True
        self.running = False
        self._send_status("Stop requested")

    def _draw_counter_info(self, frame, result: CounterResult) -> None:
        """
        Sayım bilgisini görüntünün üstüne yazar.
        """
        text = (
            f"Passengers: {result.detected_count} | "
            f"Status: {result.density_status}"
        )

        cv2.rectangle(frame, (10, 10), (590, 60), (0, 0, 0), -1)

        cv2.putText(
            frame,
            text,
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
        )

    def _get_source_name(self) -> str:
        """
        Log için kaynak adını üretir.
        """
        if isinstance(self.source, int):
            return f"camera_{self.source}"

        return Path(self.source).name

    def _send_status(self, message: str) -> None:
        """
        UI tarafına durum mesajı gönderir.
        """
        if self.status_callback is not None:
            self.status_callback(message)