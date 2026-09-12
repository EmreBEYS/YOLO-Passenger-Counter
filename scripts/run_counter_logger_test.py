import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from passenger_counter.counter import PassengerCounter
from passenger_counter.decision import get_density_status
from passenger_counter.detector import DetectionBox, PassengerDetector
from passenger_counter.event_logger import EventLogger


def make_box(x1: int, y1: int, x2: int, y2: int, confidence: float) -> DetectionBox:
    return DetectionBox(x1, y1, x2, y2, confidence, 0, "person")


def main() -> None:
    expected = {
        0: "Low Density",
        10: "Low Density",
        11: "Medium Density",
        25: "Medium Density",
        26: "High Density",
    }
    for count, status in expected.items():
        assert get_density_status(count) == status
    print("[PASS] Density decision boundaries")

    counter = PassengerCounter()
    result = counter.update([object(), object(), object()])
    assert result.detected_count == 3
    assert result.inside == 3
    assert result.density_status == "Low Density"
    print("[PASS] Passenger counter")

    main_person = make_box(0, 0, 100, 200, 0.85)
    duplicate_leg = make_box(20, 80, 40, 180, 0.30)
    separate_person = make_box(120, 0, 220, 200, 0.75)
    filtered = PassengerDetector._remove_nested_duplicates(
        [main_person, duplicate_leg, separate_person]
    )
    assert main_person in filtered
    assert separate_person in filtered
    assert duplicate_leg not in filtered
    assert len(filtered) == 2
    print("[PASS] Nested duplicate filter")

    EventLogger().write("sprint_07_test", result)
    print("[PASS] CSV event logger")
    print("Sprint 07 checks completed successfully.")


if __name__ == "__main__":
    main()
