import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import cv2
from PIL import Image, ImageTk

from config import AppConfig
from passenger_counter.video_worker import VideoWorker


class PassengerCounterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = AppConfig()
        self.source: int | str = 0
        self.stop_event = threading.Event()
        self.worker_thread: threading.Thread | None = None
        self.messages: queue.Queue[tuple] = queue.Queue(maxsize=2)
        self.preview_image: ImageTk.PhotoImage | None = None

        self.entered_var = tk.StringVar(value="0")
        self.exited_var = tk.StringVar(value="0")
        self.inside_var = tk.StringVar(value="0")
        self.source_var = tk.StringVar(value="Kamera 0")
        self.status_var = tk.StringVar(value="Hazir")

        self._build_ui()
        self.root.after(30, self._poll_messages)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self) -> None:
        self.root.title("YOLO Passenger Counter")
        self.root.geometry("1100x760")
        self.root.minsize(820, 620)

        toolbar = ttk.Frame(self.root, padding=12)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Kamera", command=self._choose_camera).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Video Sec", command=self._choose_video).pack(side="left", padx=4)
        self.start_button = ttk.Button(toolbar, text="Baslat", command=self._start)
        self.start_button.pack(side="left", padx=(20, 4))
        self.stop_button = ttk.Button(toolbar, text="Durdur", command=self._stop, state="disabled")
        self.stop_button.pack(side="left", padx=4)
        ttk.Label(toolbar, textvariable=self.source_var).pack(side="right")

        cards = ttk.Frame(self.root, padding=(12, 0, 12, 10))
        cards.pack(fill="x")
        for title, variable in (
            ("Giris", self.entered_var),
            ("Cikis", self.exited_var),
            ("Iceride", self.inside_var),
        ):
            card = ttk.LabelFrame(cards, text=title, padding=10)
            card.pack(side="left", fill="x", expand=True, padx=4)
            ttk.Label(card, textvariable=variable, font=("Segoe UI", 24, "bold")).pack()

        self.preview = ttk.Label(self.root, anchor="center", text="Goruntu bekleniyor")
        self.preview.pack(fill="both", expand=True, padx=16, pady=6)
        ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=10).pack(fill="x")

    def _choose_camera(self) -> None:
        if self._is_running():
            return
        self.source = 0
        self.source_var.set("Kamera 0")

    def _choose_video(self) -> None:
        if self._is_running():
            return
        path = filedialog.askopenfilename(
            title="Video sec",
            filetypes=[("Video dosyalari", "*.mp4 *.avi *.mov *.mkv"), ("Tum dosyalar", "*.*")],
        )
        if path:
            self.source = path
            self.source_var.set(Path(path).name)

    def _start(self) -> None:
        if self._is_running():
            return
        self.stop_event.clear()
        worker = VideoWorker(
            self.config,
            self.source,
            self.stop_event,
            self._queue_frame,
            self._queue_status,
        )
        self.worker_thread = threading.Thread(target=worker.run, daemon=True)
        self.worker_thread.start()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def _stop(self) -> None:
        self.stop_event.set()
        self.status_var.set("Durduruluyor...")

    def _is_running(self) -> bool:
        return bool(self.worker_thread and self.worker_thread.is_alive())

    def _queue_frame(self, frame, entered: int, exited: int) -> None:
        self._put_latest(("frame", frame, entered, exited))

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
                    _, frame, entered, exited = message
                    self._show_frame(frame)
                    self.entered_var.set(str(entered))
                    self.exited_var.set(str(exited))
                    self.inside_var.set(str(entered - exited))
                else:
                    self.status_var.set(message[1])
        except queue.Empty:
            pass

        if self.worker_thread and not self.worker_thread.is_alive():
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.worker_thread = None
        self.root.after(30, self._poll_messages)

    def _show_frame(self, frame) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        image.thumbnail((self.config.display_width, self.config.display_height))
        self.preview_image = ImageTk.PhotoImage(image)
        self.preview.configure(image=self.preview_image, text="")

    def _close(self) -> None:
        self.stop_event.set()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    PassengerCounterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

