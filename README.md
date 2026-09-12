# YOLO Passenger Counter

An academic desktop demonstration that detects and counts passengers from a local video or camera feed using a pretrained YOLO model.

## Final Project Status

The planned Sprint 05-08 scope is complete.

- Sprint 05: person detection, frame counting, density decisions and logging
- Sprint 06: live analytics, change-based event log and CSV session reports
- Sprint 07: stability improvements, controlled logging and automated checks
- Sprint 08: final documentation, reproducible dependencies and delivery review

## Features

- Pretrained YOLOv8s person detection; no custom training dataset required
- Camera and local video selection
- Bounding boxes and confidence scores
- Current passenger count
- Density classification:
  - 0-10 passengers: Low Density
  - 11-25 passengers: Medium Density
  - 26 or more passengers: High Density
- Nested duplicate-box filtering
- Dark English dashboard
- Live passenger-count chart
- Processed-frame, peak-count and average-count statistics
- Change-based event log
- CSV event logging and exportable session summary
- Background model loading to keep the interface responsive
- Safe video-resource cleanup and visible error messages

## Project Structure

```text
YOLO-Passenger-Counter/
├── logs/
├── passenger_counter/
│   ├── __init__.py
│   ├── counter.py
│   ├── decision.py
│   ├── detector.py
│   ├── event_logger.py
│   └── video_worker.py
├── scripts/
│   ├── run_counter_logger_test.py
│   └── run_video_worker_test.py
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

## Installation

Python 3.10 or newer is recommended.

```bash
pip install -r requirements.txt
```

The application uses the pretrained `yolov8s.pt` model. Ultralytics may download the model automatically on its first run.

## Running the Application

Run the project entry point from the repository root:

```bash
python app.py
```

Do not run modules such as `passenger_counter/detector.py` directly. They are internal application components.

Use `Camera` for the default camera or `Open Video` to select a local video file. Then select `Start Analysis`.

## Session Report

After an analysis session, open the `Event Log` tab and select `Export Session Report`. The generated CSV summary contains:

- Source name
- Session start and export timestamps
- Processed frame count
- Peak passenger count
- Average passenger count
- Final passenger count
- Final density state

## Automated Check

Run:

```bash
python scripts/run_counter_logger_test.py
```

The script checks density boundaries, passenger counting, nested duplicate filtering and CSV event logging.

## Configuration

Detection settings are defined in `config.py`. The final academic-demo defaults use:

- Model: YOLOv8s
- Confidence threshold: 0.25
- Inference image size: 960
- IoU threshold: 0.45
- Maximum detections per frame: 100
- Persistent CSV log interval: every 10 processed frames

These values provide a practical balance between accuracy and performance for crowded vehicle interiors.

## Academic Limitations

This application is a demonstration, not a production passenger-measurement or surveillance system. Results may vary because of:

- Camera angle and lens distortion
- Lighting and motion blur
- Partial occlusion between passengers
- Seats or objects that visually resemble people
- The limitations of a general-purpose pretrained model

The current count represents people detected in each frame. Unique-person tracking and reliable physical entry/exit counting are not implemented; therefore the Entered and Exited values remain zero in this version.

## Privacy

Only use footage that you are authorized to process. Faces and other personally identifiable areas must be blurred or masked before screenshots, reports or demonstrations are published. Raw passenger footage should not be committed to the repository.

## Disclaimer

This project was developed for academic testing and demonstration purposes. Any real-world use must comply with applicable privacy, consent and data-protection requirements.


## Application Screenshots

The following screenshots demonstrate the final academic dashboard. Passenger faces and other identifiable areas are anonymized where required.

### Ready State

The dashboard before a video or camera analysis begins.

![Ready dashboard](<docs/screenshots/Ekran görüntüsü 2026-09-12 085733.png>)

### Live Analytics — Light Occupancy

A low-density analysis session with real-time passenger metrics and the live chart.

![Light-occupancy live analytics](<docs/screenshots/Ekran görüntüsü 2026-09-12 085659.png>)

### Live Analytics — Multiple Detections

A passenger-detection example showing bounding boxes, confidence scores and session statistics.

![Multiple passenger detections](<docs/screenshots/Ekran görüntüsü 2026-09-12 084331.png>)

### Event Log and Report Export

The event-log view records passenger-count and density changes and provides CSV report export.

![Event log and report export](<docs/screenshots/Ekran görüntüsü 2026-09-12 085719.png>)
