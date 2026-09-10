import sys
from pathlib import Path

import cv2

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from config import AppConfig
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

    config = AppConfig()

    # Videolar data/private/videos klasöründe tutuluyor.
    video_path = config.PRIVATE_VIDEO_DIR / "yolo_demogorsel_001.mp4"

    if not video_path.exists():
        print(f"Video bulunamadı: {video_path}")
        print("Mevcut video klasörü:", config.PRIVATE_VIDEO_DIR)

        if config.PRIVATE_VIDEO_DIR.exists():
            print("Klasördeki dosyalar:")
            for file in config.PRIVATE_VIDEO_DIR.iterdir():
                print("-", file.name)

        return

    worker = VideoWorker(
        source=video_path,
        frame_callback=on_frame,
        status_callback=on_status,
        config=config,
    )

    worker.start()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()