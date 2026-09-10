from dataclasses import dataclass


@dataclass
class CounterResult:
    """
    Bir frame için yolcu sayım sonucunu temsil eder.
    """
    entered: int
    exited: int
    inside: int
    detected_count: int


class PassengerCounter:
    """
    V1 yolcu sayım sınıfı.

    Bu sürümde gerçek giriş/çıkış takibi yok.
    YOLO kaç kişi gördüyse inside değeri olarak onu gösterir.
    """

    def __init__(self) -> None:
        self.entered_total = 0
        self.exited_total = 0
        self.inside_current = 0

    def update(self, detections: list) -> CounterResult:
        detected_count = len(detections)

        self.inside_current = detected_count

        return CounterResult(
            entered=self.entered_total,
            exited=self.exited_total,
            inside=self.inside_current,
            detected_count=detected_count,
        )

    def reset(self) -> None:
        self.entered_total = 0
        self.exited_total = 0
        self.inside_current = 0