import sys
from pathlib import Path

import cv2

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from passenger_counter.video_worker import VideoWorker


worker = None


def on_frame(frame, result) -> None:
    global worker

    cv2.imshow("YOLO Passenger Counter - VideoWorker Test", frame)

    print(
        f"Detected: {result.detected_count} | "
        f"Inside: {result.inside} | "
        f"Entered: {result.entered} | "
        f"Exited: {result.exited}"
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        if worker is not None:
            worker.stop()


def on_status(message: str) -> None:
    print("[STATUS]", message)


def main() -> None:
    global worker

    if len(sys.argv) != 2:
        print("Kullanim: python scripts/run_video_worker_test.py <video_yolu>")
        return

    video_path = Path(sys.argv[1]).expanduser().resolve()
    if not video_path.is_file():
        print(f"Video bulunamadi: {video_path}")
        return

    worker = VideoWorker(
        source=video_path,
        frame_callback=on_frame,
        status_callback=on_status,
    )

    worker.start()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
