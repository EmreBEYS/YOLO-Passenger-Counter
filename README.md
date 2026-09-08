# YOLO Passenger Counter

A YOLO-based passenger counting and decision support system for public transportation and crowded environments.

This project aims to detect people in images or videos, estimate passenger density, and generate simple decision-support outputs based on the detected passenger count.

## Purpose

The main goals of this project are to:

- Detect passengers and people using YOLO
- Count people in images and video streams
- Analyze crowd density
- Generate basic decision-support outputs
- Provide anonymized demo screenshots for documentation

Example outputs:

```text
Detected Passengers: 18
Density Level: NORMAL
Decision: No additional vehicle required
```

```text
Detected Passengers: 47
Density Level: CRITICAL
Decision: Additional vehicle recommended
```

## Planned Features

- Person detection with YOLO
- Image- and video-based passenger counting
- Region-based density analysis
- Entry and exit counting
- A simple decision engine
- Blurred and anonymized demo screenshots
- Basic reporting

## Project Structure

```text
YOLO-Passenger-Counter/
├── src/
│   ├── detector/
│   ├── tracker/
│   ├── counter/
│   ├── decision/
│   └── app.py
├── configs/
├── docs/
│   └── screenshots/
├── demo/
├── scripts/
├── requirements.txt
├── .gitignore
└── README.md
```

## Data Privacy

Raw images, videos, and datasets are not included in this repository because of privacy, licensing, and ethical restrictions.

Only anonymized or blurred demo screenshots will be shared for documentation purposes.

The following folders and files should be ignored by Git:

```text
dataset/
datasets/
videos/
raw/
weights/
runs/
```

## Technologies

- Python
- YOLO
- OpenCV
- PyTorch
- NumPy

Tracking algorithms and more advanced decision mechanisms may be added in future versions.

## Status

This project is currently in the planning stage.

The first milestone is to build a working demo that detects and counts passengers in images and videos.

