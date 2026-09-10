# YOLO Passenger Counter

YOLO Passenger Counter is a lightweight computer vision demo project for detecting and counting passengers from local video or camera input.

The project uses a YOLO-based object detection model to detect people in video frames and logs passenger count information into a CSV file. It is designed as an academic/demo project and can be extended with tracking, entry-exit line counting, dashboard visualization, and real-time camera support.

## Features

- YOLO-based person detection
- Local video input support
- Basic passenger counting
- CSV event logging
- Simple Python project structure
- Privacy-first dataset handling
- Extendable architecture for future tracking and dashboard features

## Current Status

This repository currently contains the early V1 demo structure.

Completed:

- Project folder structure
- Privacy-focused data layout
- Basic passenger counter logic
- CSV event logger
- YOLO detector base
- Video worker integration draft

In Progress:

- Video worker test
- GUI integration with Tkinter

Planned:

- Real-time camera mode
- Entry/exit line counting
- Object tracking
- Dashboard charts
- Demo screenshots with anonymized faces

## Project Structure

```text
YOLO-Passenger-Counter/
├── configs/
├── data/
│   └── private/
│       ├── videos/
│       └── images/
├── demo/
├── docs/
│   └── screenshots/
├── logs/
├── passenger_counter/
│   ├── __init__.py
│   ├── counter.py
│   ├── detector.py
│   ├── event_logger.py
│   └── video_worker.py
├── scripts/
├── app.py
├── config.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Privacy Notice

This project is developed for demonstration and academic purposes.

Due to privacy and KVKK/GDPR-related concerns, raw passenger images, videos, and datasets are not included in this repository.

Any visual material used in documentation, GitHub screenshots, presentations, or reports must be anonymized. Passenger faces and personally identifiable areas should be blurred or masked before being shared publicly.

Users who want to test the system should provide their own local video files or camera input.

## Dataset Policy

This repository does not include real passenger videos or images.

Local test videos should be placed under:

```text
data/private/videos/
```

Example:

```text
data/private/videos/yolo_demogorsel_001.mp4
```

The `data/private/` directory is ignored by Git and should never be committed.

## Installation

Clone the repository:

```bash
git clone https://github.com/EmreBEYS/YOLO-Passenger-Counter.git
cd YOLO-Passenger-Counter
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Requirements

```txt
ultralytics
opencv-python
pillow
numpy
```

## Running Tests

Counter and logger test:

```bash
python scripts/run_counter_logger_test.py
```

Video worker test:

```bash
python scripts/run_video_worker_test.py
```

## Usage

Place your local video files inside:

```text
data/private/videos/
```

Then run the video worker test:

```bash
python scripts/run_video_worker_test.py
```

The system will:

1. Open the selected local video file
2. Detect people using YOLO
3. Count detected passengers per frame
4. Display detection boxes
5. Save count logs into a CSV file

## Output

Passenger count logs are stored in:

```text
logs/passenger_log.csv
```

Example CSV format:

```csv
timestamp,source,entered,exited,inside,detected_count
2026-09-10 20:30:12,yolo_demogorsel_001.mp4,0,0,3,3
```

## Roadmap

### V1 - Demo

- YOLO person detection
- Local video processing
- Passenger count display
- CSV logging
- Basic GUI

### V2 - Tracking

- Object tracking
- Unique person ID handling
- Entry/exit line counting
- Duplicate count prevention

### V3 - Dashboard

- Live charts
- Daily passenger count reports
- Exportable logs
- Improved user interface

### V4 - Deployment

- Camera stream support
- Packaged desktop app
- Performance optimization

## Disclaimer

This project is not intended to be used as a production surveillance system.

It is an academic computer vision demo focused on passenger counting. Any real-world use must follow local privacy, data protection, and consent regulations.