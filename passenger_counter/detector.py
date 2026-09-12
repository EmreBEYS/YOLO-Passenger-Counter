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

        self.model = YOLO(str(self.config.MODEL_PATH))

    def detect(self, frame) -> List[DetectionBox]:
        """
        Frame üzerinde person tespiti yapar.
        """
        if frame is None:
            return []

        results = self.model(
            frame,
            conf=self.config.CONFIDENCE_THRESHOLD,
            iou=self.config.IOU_THRESHOLD,
            imgsz=self.config.INFERENCE_SIZE,
            max_det=self.config.MAX_DETECTIONS,
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

        return self._remove_nested_duplicates(detections)

    @staticmethod
    def _remove_nested_duplicates(
        detections: List[DetectionBox],
    ) -> List[DetectionBox]:
        """Remove small, lower-confidence boxes nested inside one person box."""
        kept: List[DetectionBox] = []

        def area(box: DetectionBox) -> int:
            return max(0, box.x2 - box.x1) * max(0, box.y2 - box.y1)

        for candidate in sorted(detections, key=area, reverse=True):
            candidate_area = area(candidate)
            if candidate_area == 0:
                continue

            is_duplicate = False
            for existing in kept:
                intersection_width = max(
                    0,
                    min(candidate.x2, existing.x2)
                    - max(candidate.x1, existing.x1),
                )
                intersection_height = max(
                    0,
                    min(candidate.y2, existing.y2)
                    - max(candidate.y1, existing.y1),
                )
                covered_ratio = (
                    intersection_width * intersection_height / candidate_area
                )

                if (
                    covered_ratio >= 0.80
                    and candidate.confidence <= existing.confidence
                ):
                    is_duplicate = True
                    break

            if not is_duplicate:
                kept.append(candidate)

        return kept

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