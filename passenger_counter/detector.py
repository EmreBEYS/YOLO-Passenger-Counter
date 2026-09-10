from dataclasses import dataclass
from typing import List

import cv2
from ultralytics import YOLO

from config import AppConfig


@dataclass
class DetectionBox:
    """
    Tek bir YOLO tespit kutusunu temsil eder.
    """
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    class_id: int
    label: str


class PassengerDetector:
    """
    YOLO modeli ile kişi/yolcu tespiti yapar.
    V1 sürümünde sadece 'person' class kullanılır.
    """

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()

        # İlk çalıştırmada yolov8n.pt otomatik indirilebilir.
        self.model = YOLO(self.config.MODEL_NAME)

    def detect(self, frame) -> List[DetectionBox]:
        """
        Frame üzerinde person tespiti yapar.
        """
        if frame is None:
            return []

        results = self.model(
            frame,
            conf=self.config.CONFIDENCE_THRESHOLD,
            classes=[self.config.PERSON_CLASS_ID],
            verbose=False,
        )

        detections: List[DetectionBox] = []

        if not results:
            return detections

        result = results[0]

        if result.boxes is None:
            return detections

        for box in result.boxes:
            xyxy = box.xyxy[0].tolist()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])

            x1, y1, x2, y2 = map(int, xyxy)

            detections.append(
                DetectionBox(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confidence=confidence,
                    class_id=class_id,
                    label="person",
                )
            )

        return detections

    def draw_detections(self, frame, detections: List[DetectionBox]):
        """
        Tespit kutularını frame üzerine çizer.
        """
        if frame is None:
            return frame

        for detection in detections:
            cv2.rectangle(
                frame,
                (detection.x1, detection.y1),
                (detection.x2, detection.y2),
                (0, 255, 0),
                2,
            )

            label_text = f"{detection.label} {detection.confidence:.2f}"

            cv2.putText(
                frame,
                label_text,
                (detection.x1, max(detection.y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        return frame