import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from passenger_counter.counter import PassengerCounter
from passenger_counter.event_logger import EventLogger


def main() -> None:
    counter = PassengerCounter()
    logger = EventLogger()

    fake_detections = [
        {"label": "person", "confidence": 0.91},
        {"label": "person", "confidence": 0.88},
        {"label": "person", "confidence": 0.79},
    ]

    result = counter.update(fake_detections)

    print("Entered:", result.entered)
    print("Exited:", result.exited)
    print("Inside:", result.inside)
    print("Detected:", result.detected_count)

    logger.write("test_source", result)

    print("Log yazildi: logs/passenger_log.csv")


if __name__ == "__main__":
    main()