from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
import threading

try:
    from Foundation import NSObject, NSDistributedNotificationCenter
    import objc
except ModuleNotFoundError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyobjc"])
    from Foundation import NSObject, NSDistributedNotificationCenter
    import objc

def is_dark_mode():
    palette = QApplication.palette()
    return palette.color(QPalette.Window).value() < 128

class ThemeMonitor(NSObject):
    def initWithCallback_(self, callback):
        self = objc.super(ThemeMonitor, self).init()
        if self is None:
            return None
        self.callback = callback
        center = NSDistributedNotificationCenter.defaultCenter()
        center.addObserver_selector_name_object_(
            self,
            objc.selector(self.theme_changed_, signature=b'v@:@'),
            "AppleInterfaceThemeChangedNotification",
            None
        )
        return self

    def theme_changed_(self, notification, info):
        threading.Timer(0, self.callback).start()

class UpdateWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Güncelleme")
        self.setFixedSize(400, 250)

        # Modern background color and layout spacing/padding
        self.setStyleSheet("background-color: #f9f9f9;")

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(30)

        self.version_label = QLabel("Bafetto 2.3.1")
        self.version_label.setAlignment(Qt.AlignCenter)
        # Modern version label style
        self.version_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #333; letter-spacing: 1px;"
        )

        self.update_button = QPushButton("Güncelle")
        self.update_button.setFixedWidth(150)
        self.update_button.clicked.connect(self.on_update_clicked)
        # Modern button style with hover
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        self.layout.addWidget(self.version_label)
        self.layout.addWidget(self.update_button, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        self.update_styles()
        self.start_theme_monitor()

    def on_update_clicked(self):
        print("Güncelle butonuna basıldı.")

    def start_theme_monitor(self):
        try:
            self._theme_monitor = ThemeMonitor.alloc().initWithCallback_(self.update_styles)
        except Exception as e:
            print("Tema takibi başlatılamadı:", e)

    def showEvent(self, event):
        self.update_styles()
        super().showEvent(event)

    def update_styles(self):
        # Optionally, you can adapt the modern style for dark mode here if desired.
        pass
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = UpdateWindow()
    window.show()
    sys.exit(app.exec_())