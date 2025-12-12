import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QTextEdit,
    QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QTimeEdit
)
from PyQt5.QtCore import QTime, QThread, pyqtSignal, QTimer

from src import F_MainProcess as FMP
from src import D_Utils as DU
import time
from datetime import datetime

# ---------- Worker Thread ----------
class MusicSenderThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, gui_self):
        super().__init__()
        self.gui_self = gui_self
        self.running = True


    def run(self):
        last_run_date = None
        while self.running:
            now = datetime.now().time()
            start_time = self.gui_self.start_time_edit.time().toPyTime()
            end_time = self.gui_self.end_time_edit.time().toPyTime()

            # بررسی اینکه داخل بازه هستیم
            in_range = False
            if start_time < end_time:
                in_range = start_time <= now <= end_time
            else:
                # بازه عبور از نیمه‌شب
                in_range = now >= start_time or now <= end_time

            today = datetime.now().date()
            if in_range and last_run_date != today:
                # اجرا در Thread جداگانه
                FMP.start_processing(self.gui_self)
                last_run_date = today

            # جلوگیری از استفاده 100% CPU
            time.sleep(1)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
        self.finished_signal.emit()


# ---------- GUI ----------
class MusicBotGui(QWidget):
    def __init__(self):
        super().__init__()

        self.music_folder = None
        self.image_folder = None

        self.config = DU.load_config()
        self.worker_thread = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Music Bot")
        layout = QVBoxLayout()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # هر ۱ ثانیه

        self.lbl_clock = QLabel("Time: --:--:--")
        font = self.lbl_clock.font()
        font.setPointSize(20)
        font.setBold(True)
        self.lbl_clock.setFont(font)


        # --- Output box
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        # --- Folder selection labels
        self.lbl_music = QLabel("Folder Music: Not selected")
        if self.config["music_folder"]:
            self.lbl_music.setText(f"Folder Music: {self.config['music_folder']}")

        self.lbl_images = QLabel("Folder Images: Not selected")
        image_folder = self.config.get("image_folder", "")
        if image_folder:
            self.lbl_images.setText(f"Folder Images: {self.config['image_folder']}")

        # --- Buttons
        self.btn_music = QPushButton("Select Music Folder")
        self.btn_images = QPushButton("Select Images Folder")


        self.NumMusic = QHBoxLayout()
        self.NumMusic.addWidget(QLabel("Num Music: "))

        self.daily_count = QLineEdit()
        self.daily_count.setText(str(self.config.get("daily_count", 1)))

        self.NumMusic.addWidget(self.daily_count)

        # --- Time Range
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Start Time:"))
        self.start_time_edit = QTimeEdit()
        start = self.config.get("start_time", "09:00")
        self.start_time_edit.setTime(QTime.fromString(start, "HH:mm"))
        time_layout.addWidget(self.start_time_edit)

        time_layout.addWidget(QLabel("End Time:"))
        self.end_time_edit = QTimeEdit()
        end = self.config.get("end_time", "11:00")
        self.end_time_edit.setTime(QTime.fromString(end, "HH:mm"))
        time_layout.addWidget(self.end_time_edit)

        # ---------------- Telegram Settings ----------------


        tele_layout = QVBoxLayout()

        # Bot Token
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Bot Token:"))
        self.txt_token = QLineEdit()
        self.txt_token.setText(self.config.get("telegram_token", ""))
        h1.addWidget(self.txt_token)
        tele_layout.addLayout(h1)

        # Chat ID
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Chat ID:"))
        self.txt_chatid = QLineEdit()
        self.txt_chatid.setText(str(self.config.get("telegram_chat_id", "")))
        h2.addWidget(self.txt_chatid)
        tele_layout.addLayout(h2)

        # Delay
        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Delay (sec):"))
        self.txt_delay = QLineEdit()
        self.txt_delay.setText(str(self.config.get("send_delay", 1)))
        h3.addWidget(self.txt_delay)
        tele_layout.addLayout(h3)

        # --- Buttons
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")


        layout.addWidget(self.lbl_clock)

        # --- Add widgets
        layout.addWidget(self.output)
        layout.addWidget(QLabel("Telegram Settings:"))
        layout.addWidget(self.lbl_music)
        layout.addWidget(self.btn_music)
        layout.addWidget(self.lbl_images)
        layout.addWidget(self.btn_images)
        layout.addLayout(self.NumMusic)
        layout.addLayout(time_layout)
        layout.addLayout(tele_layout)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)

        self.setLayout(layout)

        # --- Connect events
        self.btn_music.clicked.connect(self.select_music_folder)
        self.btn_images.clicked.connect(self.select_image_folder)
        self.btn_start.clicked.connect(self.start_thread)
        self.btn_stop.clicked.connect(self.stop_thread)

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.lbl_clock.setText(f"Time: {now}")

    def select_music_folder(self):
        self.config['music_folder'] = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if self.config['music_folder']:
            self.lbl_music.setText(f"Folder Music: {self.config['music_folder']}")

    def select_image_folder(self):
        self.config["image_folder"] = QFileDialog.getExistingDirectory(self, "Select Images Folder")
        if self.config["image_folder"]:
            self.lbl_images.setText(f"Folder Images: {self.config['image_folder']}")

    def save_settings(self):
        try:
            self.config["daily_count"] = int(self.daily_count.text())
            self.config["send_delay"] = float(self.txt_delay.text())
        except:
            QMessageBox.warning(self, "Error", "Please enter a number")
            return

        self.config["start_time"] = self.start_time_edit.time().toString("HH:mm")
        self.config["end_time"] = self.end_time_edit.time().toString("HH:mm")
        self.config["telegram_token"] = self.txt_token.text().strip()
        self.config["telegram_chat_id"] = self.txt_chatid.text().strip()

        DU.save_config(self.config)
        QMessageBox.information(self, "Saved", "Saving successfully")

    # ---------- Start/Stop Thread ----------
    def start_thread(self):
        self.save_settings()
        if self.worker_thread is None or not self.worker_thread.isRunning():
            self.worker_thread = MusicSenderThread(self)
            self.worker_thread.finished_signal.connect(lambda: print("Thread finished"))
            self.worker_thread.start()
            self.output.append(">>> Music sending thread started")

    def stop_thread(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.output.append(">>> Music sending thread stopped")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MusicBotGui()
    # gui.resize(500, 500)
    gui.show()
    sys.exit(app.exec_())
