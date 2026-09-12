import csv
import queue
import threading
import tkinter as tk
from collections import deque
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk

import cv2
from PIL import Image, ImageTk

from config import AppConfig
from passenger_counter.video_worker import VideoWorker


BG = "#202124"
PANEL = "#2b2d31"
PANEL_ALT = "#33363c"
BORDER = "#44474e"
TEXT = "#f1f3f4"
MUTED = "#aeb4bd"
ACCENT = "#5b8def"
GREEN = "#42c77a"
AMBER = "#f4b942"
RED = "#ef6461"


class PassengerHistoryChart(tk.Canvas):
    """Small dependency-free live chart for recent passenger counts."""

    def __init__(self, master) -> None:
        super().__init__(
            master,
            background=PANEL,
            highlightthickness=1,
            highlightbackground=BORDER,
            height=330,
        )
        self.values: deque[int] = deque(maxlen=90)
        self.bind("<Configure>", lambda _event: self.redraw())

    def add_value(self, value: int) -> None:
        self.values.append(value)
        self.redraw()

    def clear(self) -> None:
        self.values.clear()
        self.redraw()

    def redraw(self) -> None:
        self.delete("all")
        width = max(self.winfo_width(), 320)
        height = max(self.winfo_height(), 220)
        left, top, right, bottom = 48, 38, width - 20, height - 42

        self.create_text(
            width / 2,
            18,
            text="Passenger Count History",
            fill=TEXT,
            font=("Segoe UI", 12, "bold"),
        )

        max_value = max(30, max(self.values, default=0))
        for step in range(5):
            y = top + (bottom - top) * step / 4
            label = round(max_value * (4 - step) / 4)
            self.create_line(left, y, right, y, fill="#3f4248")
            self.create_text(left - 10, y, text=str(label), fill=MUTED, anchor="e")

        self.create_line(left, top, left, bottom, fill="#747982")
        self.create_line(left, bottom, right, bottom, fill="#747982")

        if len(self.values) < 2:
            self.create_text(
                (left + right) / 2,
                (top + bottom) / 2,
                text="Start analysis to display live data",
                fill=MUTED,
                font=("Segoe UI", 10),
            )
            return

        values = list(self.values)
        points: list[float] = []
        for index, value in enumerate(values):
            x = left + (right - left) * index / (len(values) - 1)
            y = bottom - (bottom - top) * value / max_value
            points.extend((x, y))

        self.create_line(*points, fill=ACCENT, width=3, smooth=True)
        self.create_oval(
            points[-2] - 4,
            points[-1] - 4,
            points[-2] + 4,
            points[-1] + 4,
            fill=GREEN,
            outline="",
        )
        self.create_text(
            right,
            bottom + 22,
            text=f"Last {len(values)} updates",
            fill=MUTED,
            anchor="e",
        )


class PassengerCounterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = AppConfig()
        self.source: int | str = 0
        self.worker_thread: threading.Thread | None = None
        self.worker: VideoWorker | None = None
        self.messages: queue.Queue[tuple] = queue.Queue(maxsize=4)
        self.preview_image: ImageTk.PhotoImage | None = None

        self.entered_var = tk.StringVar(value="0")
        self.exited_var = tk.StringVar(value="0")
        self.inside_var = tk.StringVar(value="0")
        self.density_var = tk.StringVar(value="Low Density")
        self.source_var = tk.StringVar(value="Camera 0")
        self.status_var = tk.StringVar(value="Ready")
        self.frames_var = tk.StringVar(value="0")
        self.peak_var = tk.StringVar(value="0")
        self.average_var = tk.StringVar(value="0.0")

        self.processed_frames = 0
        self.total_passengers = 0
        self.peak_passengers = 0
        self.last_event_count: int | None = None
        self.session_started_at: datetime | None = None

        self._configure_window()
        self._configure_styles()
        self._build_ui()
        self.root.after(30, self._poll_messages)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _configure_window(self) -> None:
        self.root.title("YOLO Passenger Counter")
        self.root.geometry("1440x840")
        self.root.minsize(1120, 700)
        self.root.configure(background=BG)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("PanelAlt.TFrame", background=PANEL_ALT)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("PanelMuted.TLabel", background=PANEL, foreground=MUTED)
        style.configure("Header.TLabel", font=("Segoe UI", 17, "bold"))
        style.configure("Section.TLabel", background=PANEL, font=("Segoe UI", 11, "bold"))
        style.configure("MetricValue.TLabel", background=PANEL_ALT, font=("Segoe UI", 24, "bold"))
        style.configure("MetricTitle.TLabel", background=PANEL_ALT, foreground=MUTED)
        style.configure(
            "TButton",
            background="#45484f",
            foreground=TEXT,
            padding=(13, 8),
            borderwidth=0,
        )
        style.map("TButton", background=[("active", "#555963"), ("disabled", "#34363b")])
        style.configure("Accent.TButton", background=ACCENT, foreground="white")
        style.map("Accent.TButton", background=[("active", "#76a0f2"), ("disabled", "#3d4d6d")])
        style.configure("Danger.TButton", background="#a94747", foreground="white")
        style.map("Danger.TButton", background=[("active", "#c15757"), ("disabled", "#4b3838")])
        style.configure("TLabelframe", background=PANEL, bordercolor=BORDER, relief="solid")
        style.configure("TLabelframe.Label", background=PANEL, foreground=TEXT, font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=MUTED, padding=(18, 9))
        style.map("TNotebook.Tab", background=[("selected", PANEL_ALT)], foreground=[("selected", TEXT)])
        style.configure(
            "Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=TEXT,
            rowheight=28,
            bordercolor=BORDER,
        )
        style.configure("Treeview.Heading", background=PANEL_ALT, foreground=TEXT, relief="flat")
        style.map("Treeview", background=[("selected", "#3f5f91")])

    def _build_ui(self) -> None:
        header = ttk.Frame(self.root, padding=(18, 13))
        header.pack(fill="x")
        ttk.Label(header, text="YOLO Passenger Counter", style="Header.TLabel").pack(side="left")
        ttk.Label(
            header,
            text="SPRINT 05  •  LIVE DETECTION DASHBOARD",
            style="Muted.TLabel",
        ).pack(side="left", padx=18)
        self.source_label = tk.Label(
            header,
            textvariable=self.source_var,
            background=PANEL_ALT,
            foreground=TEXT,
            padx=14,
            pady=6,
            font=("Segoe UI", 9, "bold"),
        )
        self.source_label.pack(side="right")

        separator = tk.Frame(self.root, background=BORDER, height=1)
        separator.pack(fill="x")

        body = ttk.Frame(self.root, padding=12)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=11, uniform="dashboard")
        body.columnconfigure(1, weight=9, uniform="dashboard")
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left.grid_propagate(False)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)

        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right.grid_propagate(False)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        self._build_controls(left)
        self._build_metrics(left)
        self._build_preview(left)
        self._build_analytics(right)

        status_bar = ttk.Frame(self.root, style="Panel.TFrame", padding=(15, 8))
        status_bar.pack(fill="x", side="bottom")
        self.status_dot = tk.Label(status_bar, text="●", background=PANEL, foreground=GREEN)
        self.status_dot.pack(side="left")
        ttk.Label(status_bar, textvariable=self.status_var, style="Panel.TLabel").pack(side="left", padx=7)
        ttk.Label(status_bar, text="YOLOv8 • Person detection", style="PanelMuted.TLabel").pack(side="right")

    def _build_controls(self, parent) -> None:
        section = ttk.LabelFrame(parent, text="  Analysis Controls  ", padding=12)
        section.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(section, text="Camera", command=self._choose_camera).pack(side="left", padx=(0, 7))
        ttk.Button(section, text="Open Video", command=self._choose_video).pack(side="left", padx=7)
        self.start_button = ttk.Button(
            section,
            text="Start Analysis",
            style="Accent.TButton",
            command=self._start,
        )
        self.start_button.pack(side="left", padx=(18, 7))
        self.stop_button = ttk.Button(
            section,
            text="Stop",
            style="Danger.TButton",
            command=self._stop,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=7)
        ttk.Button(section, text="Reset", command=self._reset_dashboard).pack(side="left", padx=(18, 0))

    def _build_metrics(self, parent) -> None:
        metrics = ttk.Frame(parent)
        metrics.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for column in range(4):
            metrics.columnconfigure(column, weight=1)

        cards = (
            ("ENTERED", self.entered_var),
            ("EXITED", self.exited_var),
            ("CURRENT", self.inside_var),
            ("DENSITY", self.density_var),
        )
        for column, (title, variable) in enumerate(cards):
            card = ttk.Frame(metrics, style="PanelAlt.TFrame", padding=(12, 10))
            card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 5, 0))
            ttk.Label(card, text=title, style="MetricTitle.TLabel").pack(anchor="w")
            label = ttk.Label(card, textvariable=variable, style="MetricValue.TLabel")
            label.pack(anchor="w", pady=(3, 0))
            if title == "DENSITY":
                self.density_label = label

    def _build_preview(self, parent) -> None:
        section = ttk.LabelFrame(parent, text="  Live Camera / Video Feed  ", padding=8)
        section.grid(row=2, column=0, sticky="nsew")
        section.columnconfigure(0, weight=1)
        section.rowconfigure(0, weight=1)

        self.preview = tk.Label(
            section,
            text="No video feed\n\nSelect a camera or open a video to begin",
            background="#111317",
            foreground=MUTED,
            font=("Segoe UI", 11),
            compound="center",
        )
        self.preview.grid(row=0, column=0, sticky="nsew")

    def _build_analytics(self, parent) -> None:
        notebook = ttk.Notebook(parent)
        notebook.grid(row=0, column=0, sticky="nsew")

        analytics_tab = ttk.Frame(notebook, style="Panel.TFrame", padding=12)
        log_tab = ttk.Frame(notebook, style="Panel.TFrame", padding=12)
        notebook.add(analytics_tab, text="Live Analytics")
        notebook.add(log_tab, text="Event Log")

        analytics_tab.columnconfigure(0, weight=1)
        analytics_tab.rowconfigure(2, weight=1)

        summary = ttk.Frame(analytics_tab, style="PanelAlt.TFrame", padding=14)
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(summary, text="CURRENT OCCUPANCY", style="MetricTitle.TLabel").pack(anchor="w")
        self.analytics_count = tk.Label(
            summary,
            textvariable=self.inside_var,
            background=PANEL_ALT,
            foreground=GREEN,
            font=("Segoe UI", 34, "bold"),
        )
        self.analytics_count.pack(side="left", pady=(5, 0))
        self.analytics_density = tk.Label(
            summary,
            textvariable=self.density_var,
            background="#244735",
            foreground="#86e3ad",
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=6,
        )
        self.analytics_density.pack(side="right", pady=(12, 0))

        stats_bar = ttk.Frame(analytics_tab, style="Panel.TFrame")
        stats_bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        for column in range(3):
            stats_bar.columnconfigure(column, weight=1)
        for column, (title, variable) in enumerate(
            (
                ("PROCESSED FRAMES", self.frames_var),
                ("PEAK COUNT", self.peak_var),
                ("AVERAGE COUNT", self.average_var),
            )
        ):
            card = ttk.Frame(stats_bar, style="PanelAlt.TFrame", padding=10)
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else 5, 0),
            )
            ttk.Label(card, text=title, style="MetricTitle.TLabel").pack()
            ttk.Label(card, textvariable=variable, style="Section.TLabel").pack(pady=(4, 0))

        self.chart = PassengerHistoryChart(analytics_tab)
        self.chart.grid(row=2, column=0, sticky="nsew")

        log_tab.columnconfigure(0, weight=1)
        log_tab.rowconfigure(1, weight=1)
        ttk.Label(log_tab, text="Recent Detection Events", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        ttk.Button(
            log_tab,
            text="Export Session Report",
            command=self._export_report,
        ).grid(row=0, column=0, sticky="e", pady=(0, 10))
        columns = ("time", "count", "density")
        self.event_table = ttk.Treeview(log_tab, columns=columns, show="headings")
        self.event_table.heading("time", text="Time")
        self.event_table.heading("count", text="Passengers")
        self.event_table.heading("density", text="Density")
        self.event_table.column("time", width=110, anchor="center")
        self.event_table.column("count", width=100, anchor="center")
        self.event_table.column("density", width=150, anchor="center")
        self.event_table.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(log_tab, orient="vertical", command=self.event_table.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.event_table.configure(yscrollcommand=scrollbar.set)

    def _choose_camera(self) -> None:
        if self._is_running():
            return
        self.source = 0
        self.source_var.set("Camera 0")
        self.status_var.set("Camera 0 selected")

    def _choose_video(self) -> None:
        if self._is_running():
            return
        path = filedialog.askopenfilename(
            title="Select a video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")],
        )
        if path:
            self.source = path
            self.source_var.set(Path(path).name)
            self.status_var.set(f"Selected: {Path(path).name}")

    def _start(self) -> None:
        if self._is_running():
            return
        self._reset_session_stats()
        self.session_started_at = datetime.now()
        self.worker = VideoWorker(
            source=self.source,
            frame_callback=self._queue_frame,
            status_callback=self._queue_status,
            config=self.config,
        )
        self.worker_thread = threading.Thread(target=self.worker.start, daemon=True)
        self.worker_thread.start()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_dot.configure(foreground=AMBER)
        self.status_var.set("Starting analysis...")

    def _stop(self) -> None:
        if self.worker is not None:
            self.worker.stop()
        self.status_dot.configure(foreground=AMBER)
        self.status_var.set("Stopping analysis...")

    def _reset_dashboard(self) -> None:
        if self._is_running():
            return
        self._reset_session_stats()
        self._set_density_colors("Low Density")
        self.status_var.set("Dashboard reset")

    def _reset_session_stats(self) -> None:
        self.entered_var.set("0")
        self.exited_var.set("0")
        self.inside_var.set("0")
        self.density_var.set("Low Density")
        self.frames_var.set("0")
        self.peak_var.set("0")
        self.average_var.set("0.0")
        self.processed_frames = 0
        self.total_passengers = 0
        self.peak_passengers = 0
        self.last_event_count = None
        self.session_started_at = None
        self.chart.clear()
        for item in self.event_table.get_children():
            self.event_table.delete(item)

    def _is_running(self) -> bool:
        return bool(self.worker_thread and self.worker_thread.is_alive())

    def _queue_frame(self, frame, result) -> None:
        self._put_latest(("frame", frame, result))

    def _queue_status(self, message: str) -> None:
        self._put_latest(("status", message))

    def _put_latest(self, message: tuple) -> None:
        try:
            self.messages.put_nowait(message)
        except queue.Full:
            try:
                self.messages.get_nowait()
            except queue.Empty:
                pass
            self.messages.put_nowait(message)

    def _poll_messages(self) -> None:
        try:
            while True:
                message = self.messages.get_nowait()
                if message[0] == "frame":
                    _, frame, result = message
                    self._show_frame(frame)
                    self._update_session_stats(result.detected_count)
                    self.entered_var.set(str(result.entered))
                    self.exited_var.set(str(result.exited))
                    self.inside_var.set(str(result.inside))
                    self.density_var.set(result.density_status)
                    self._set_density_colors(result.density_status)
                    self.chart.add_value(result.detected_count)
                    self._add_event(result.detected_count, result.density_status)
                    self.status_dot.configure(foreground=GREEN)
                    self.status_var.set("Analysis running")
                else:
                    self.status_var.set(message[1])
        except queue.Empty:
            pass

        if self.worker_thread and not self.worker_thread.is_alive():
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.worker_thread = None
            self.worker = None
            self.status_dot.configure(foreground=MUTED)
        self.root.after(30, self._poll_messages)

    def _show_frame(self, frame) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        max_width = max(self.preview.winfo_width() - 16, 320)
        max_height = max(self.preview.winfo_height() - 16, 240)
        max_width = min(max_width, self.config.DISPLAY_WIDTH)
        max_height = min(max_height, self.config.DISPLAY_HEIGHT)
        image.thumbnail((max_width, max_height))
        self.preview_image = ImageTk.PhotoImage(image)
        self.preview.configure(image=self.preview_image, text="")

    def _set_density_colors(self, status: str) -> None:
        colors = {
            "Low Density": (GREEN, "#244735", "#86e3ad"),
            "Medium Density": (AMBER, "#55451f", "#ffd873"),
            "High Density": (RED, "#592f31", "#ff9b98"),
        }
        value_color, badge_bg, badge_fg = colors.get(status, (TEXT, PANEL_ALT, TEXT))
        self.density_label.configure(foreground=value_color)
        self.analytics_count.configure(foreground=value_color)
        self.analytics_density.configure(background=badge_bg, foreground=badge_fg)

    def _update_session_stats(self, count: int) -> None:
        self.processed_frames += 1
        self.total_passengers += count
        self.peak_passengers = max(self.peak_passengers, count)
        average = self.total_passengers / self.processed_frames
        self.frames_var.set(str(self.processed_frames))
        self.peak_var.set(str(self.peak_passengers))
        self.average_var.set(f"{average:.1f}")

    def _add_event(self, count: int, density: str) -> None:
        if count == self.last_event_count:
            return
        self.last_event_count = count
        self.event_table.insert("", 0, values=(datetime.now().strftime("%H:%M:%S"), count, density))
        children = self.event_table.get_children()
        if len(children) > 200:
            self.event_table.delete(children[-1])

    def _export_report(self) -> None:
        if self.processed_frames == 0:
            self.status_var.set("No session data to export")
            return

        path = filedialog.asksaveasfilename(
            title="Export session report",
            defaultextension=".csv",
            initialfile=f"passenger_report_{datetime.now():%Y%m%d_%H%M%S}.csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return

        average = self.total_passengers / self.processed_frames
        with open(path, "w", newline="", encoding="utf-8") as report_file:
            writer = csv.writer(report_file)
            writer.writerow(["metric", "value"])
            writer.writerow(["source", self.source_var.get()])
            writer.writerow([
                "session_started",
                self.session_started_at.isoformat(timespec="seconds")
                if self.session_started_at
                else "",
            ])
            writer.writerow(["exported_at", datetime.now().isoformat(timespec="seconds")])
            writer.writerow(["processed_frames", self.processed_frames])
            writer.writerow(["peak_passenger_count", self.peak_passengers])
            writer.writerow(["average_passenger_count", f"{average:.2f}"])
            writer.writerow(["final_passenger_count", self.inside_var.get()])
            writer.writerow(["final_density", self.density_var.get()])

        self.status_var.set(f"Report exported: {Path(path).name}")

    def _close(self) -> None:
        if self.worker is not None:
            self.worker.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    PassengerCounterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()