import sys
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QWidget, QGridLayout, QFrame, QVBoxLayout, QScrollArea, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtSvg import QSvgWidget

class YonetimWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Navbar oluştur
        navbar = QWidget(self)
        navbar.setFixedHeight(50)
        navbar.setStyleSheet("background-color: white; border: none;")
        navbar_layout = QVBoxLayout(navbar)
        navbar_layout.setContentsMargins(15, 5, 0, 5)

        back_button_container = QWidget(navbar)
        back_button_layout = QHBoxLayout()
        back_button_layout.setContentsMargins(0, 0, 0, 0)
        back_button_layout.setSpacing(5)

        back_button = QPushButton("Geri")
        back_button.setIcon(QtGui.QIcon("svg/back.svg"))
        back_button.setIconSize(QtCore.QSize(24, 24))
        back_button.setStyleSheet("background-color: transparent; border: none; font-size: 14px; color: #ff4d4d;")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.handle_back)

        back_button_layout.addWidget(back_button)

        back_button_container.setLayout(back_button_layout)

        # Use HBox layout to center the title properly
        nav_content_layout = QHBoxLayout()
        nav_content_layout.setContentsMargins(0, 0, 0, 0)
        nav_content_layout.setSpacing(0)

        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(back_button_container)
        left_layout.addStretch()

        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        navbar_title = QLabel("Yönetim Paneli", navbar)
        navbar_title.setStyleSheet("font-weight: 400; font-size: 18px; color: black; text-decoration: none;")
        center_layout.addStretch()
        center_layout.addWidget(navbar_title)
        center_layout.addStretch()

        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addStretch()

        nav_content_layout.addWidget(left_container)
        nav_content_layout.addWidget(center_container)
        nav_content_layout.addWidget(right_container)

        navbar_layout.addLayout(nav_content_layout)

        self.setWindowTitle("Yönetim")
        self.setGeometry(0, 0, 1200, 600)
        # Set window width to 90% of the screen width
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        window_width = int(screen_width * 0.8)
        self.setGeometry(0, 0, window_width, 600)

        # Merkezi widget oluştur
        central_widget = QWidget(self)
        central_widget.setMinimumWidth(window_width)
        central_widget.setMaximumWidth(screen_width)
        # Merkezi widget'ı yatayda ortalamak için bir kapsayıcı ekle
        central_widget_container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.addWidget(central_widget, alignment=Qt.AlignHCenter)
        central_widget_container.setLayout(container_layout)
        
        # Kartlar için ızgara düzenini ayarla
        main_layout = QGridLayout()
        central_widget.setLayout(main_layout)

        # Kartları oluştur
        card1 = self.create_card("Toplam Ciro", "")
        card2 = self.create_card("Email", "john.doe@example.com")
        card3 = self.create_card("Mutfak ürün siparişi", "")
        card4 = self.create_card("Card 4", "Content 4")
        card5 = self.create_card("Kurye Takibi", "")
        card6 = self.create_card("Personel Yönetimi", "")
        card7 = self.create_card("Programı Güncelle", "")
        card8 = self.create_card("Diğer Ayarlar", "")

        # Kartları düzene ekle ve uygun şekilde boyutlandır
        main_layout.addWidget(card1, 0, 0, 1, 1)  # 0. satır, 0. sütun, 1 satır, 1 sütun kaplar
        main_layout.addWidget(card2, 0, 1, 1, 2)  # 0. satır, 1. sütun, 1 satır, 2 sütun kaplar
        main_layout.addWidget(card3, 1, 0, 1, 2)  # 1. satır, 0. sütun, 1 satır, 2 sütun kaplar
        main_layout.addWidget(card4, 1, 2, 1, 1)  # 1. satır, 2. sütun, 1 satır, 1 sütun kaplar
        main_layout.addWidget(card5, 2, 0, 1, 1)  # 2. satır, 0. sütun, 1 satır, 1 sütun kaplar
        main_layout.addWidget(card6, 2, 1, 1, 2)  # 2. satır, 1. sütun, 1 satır, 2 sütun kaplar
        main_layout.addWidget(card7, 3, 0, 1, 1)  # 3. satır, 0. sütun, 1 satır, 1 sütun kaplar
        main_layout.addWidget(card8, 3, 1, 1, 2)  # 3. satır, 1. sütun, 1 satır, 2 sütun kaplar

        # Sütun genişliklerini orantılı olarak ayarla
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        main_layout.setColumnStretch(2, 1)

        # Satır yüksekliklerini orantılı olarak ayarla
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 1)
        main_layout.setRowStretch(3, 1)

        # QScrollArea oluştur ve central_widget_container'ı içine yerleştir
        scroll_area = QScrollArea(self)
        scroll_area.setWidget(central_widget_container)
        scroll_area.setWidgetResizable(True)  # Widget'ın boyutunu scroll alanına göre ayarlar
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Yatay kaydırmayı kapat
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Dikey kaydırmayı gerektiğinde göster

        # ScrollArea’yı ana pencereye ekle
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        central_widget_main = QWidget()
        central_layout.addWidget(navbar)
        central_layout.addWidget(scroll_area)
        central_widget_main.setLayout(central_layout)

        self.setCentralWidget(central_widget_main)

    def create_card(self, title, content):
        card = QFrame()
        card.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            padding: 30px 20px;
            margin: 5px;
        """)
        layout = QVBoxLayout()

        # Başlık etiketi
        if title not in ["Email", "Card 4", "Kurye Takibi", "Personel Yönetimi", "Programı Güncelle", "Diğer Ayarlar"]:
            title_label = QLabel(f"<b>{title}</b>")
            if title == "Toplam Ciro":
                title_label.setStyleSheet("color: black; font-size: 18px;")
            else:
                title_label.setStyleSheet("color: black;")
            layout.addWidget(title_label)

        # İçerik etiketi (SVG veya başka özel ikon yok)
        if title == "Toplam Ciro":
            self.ciro_label = QLabel("0 TL")
            self.ciro_label.setStyleSheet("color: black; font-size: 32px; font-weight: 300;")
            layout.addWidget(self.ciro_label)

            # Use QPropertyAnimation on a dummy QObject property, since QLabel doesn't have 'text' as a property
            # We'll animate an integer value and update the label in a slot
            self._ciro_value_anim = QtCore.QVariantAnimation()
            self._ciro_value_anim.setStartValue(0)
            self._ciro_value_anim.setEndValue(22000)
            self._ciro_value_anim.setDuration(1500)
            self._ciro_value_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
            self._ciro_value_anim.valueChanged.connect(self.update_ciro_label)
            QtCore.QTimer.singleShot(300, self._ciro_value_anim.start)
        else:
            if title == "Email":
                import matplotlib.pyplot as plt
                from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
                from matplotlib.figure import Figure
                import numpy as np

                fig = Figure()
                canvas = FigureCanvas(fig)
                canvas.setMinimumHeight(200)
                ax = fig.add_subplot(111)

                days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
                revenue = np.random.randint(2000, 7000, size=7)
                ax.bar(days, revenue, color="#4CAF50", width=0.6)
                ax.set_xticks(range(len(days)))
                ax.set_xticklabels(days)

                ax.set_title("30 Günlük Ciro")
                ax.set_ylabel("TL")
                fig.subplots_adjust(left=0.15, right=0.98, top=0.88, bottom=0.1)

                layout.addWidget(canvas)
            elif title == "Mutfak ürün siparişi":
                content_layout = QHBoxLayout()
                content_layout.setContentsMargins(0, 0, 0, 0)

                text_area = QWidget()
                text_layout = QVBoxLayout(text_area)
                text_layout.setContentsMargins(0, 0, 0, 0)
                text_label = QLabel(content)
                text_label.setStyleSheet("color: black;")
                text_layout.addWidget(text_label)
                content_layout.addWidget(text_area, stretch=1)

                svg_widget = QSvgWidget("svg/mutfak.svg")
                svg_widget.setFixedSize(150, 150)
                content_layout.addWidget(svg_widget, alignment=Qt.AlignRight)

                layout.addLayout(content_layout)
            elif title == "Card 4":
                title_label = QLabel("<b>QR Menu</b>")
                title_label.setStyleSheet("color: black;")
                layout.insertWidget(0, title_label)

                qr_widget = QSvgWidget("svg/qr.svg")
                qr_widget.setFixedSize(150, 150)
                layout.addWidget(qr_widget, alignment=Qt.AlignCenter)
            elif title == "Kurye Takibi":
                title_label = QLabel("<b>Kurye Takibi</b>")
                title_label.setStyleSheet("color: black;")
                layout.insertWidget(0, title_label)

                motor_widget = QSvgWidget("svg/motor.svg")
                motor_widget.setFixedSize(150, 150)
                layout.addWidget(motor_widget, alignment=Qt.AlignCenter)
            elif title == "Personel Yönetimi":
                title_label = QLabel("<b>Personel Yönetimi</b>")
                title_label.setStyleSheet("color: black;")
                layout.insertWidget(0, title_label)

                personel_widget = QSvgWidget("svg/personel.svg")
                personel_widget.setFixedSize(150, 150)
                layout.addWidget(personel_widget, alignment=Qt.AlignCenter)
            elif title == "Programı Güncelle":
                title_label = QLabel("<b>Programı Güncelle</b>")
                title_label.setStyleSheet("color: black;")
                layout.insertWidget(0, title_label)

                update_widget = QSvgWidget("svg/guncelle.svg")
                update_widget.setFixedSize(150, 150)
                layout.addWidget(update_widget, alignment=Qt.AlignCenter)
            elif title == "Diğer Ayarlar":
                title_label = QLabel("<b>Diğer Ayarlar</b>")
                title_label.setStyleSheet("color: black;")
                layout.insertWidget(0, title_label)

                settings_widget = QSvgWidget("svg/ayarlar.svg")
                settings_widget.setFixedSize(150, 150)
                layout.addWidget(settings_widget, alignment=Qt.AlignCenter)
            else:
                content_label = QLabel(content)
                content_label.setStyleSheet("color: black;")
                layout.addWidget(content_label)

        if title != "Email":
            # Button container to prevent layout jump on hover
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)

            detail_button = QPushButton("Detayları gör")
            detail_button.setStyleSheet("background-color: transparent; color: #007bff; border: 1px solid #007bff; padding: 10px 15px; border-radius: 5px;")
            detail_button.setCursor(Qt.PointingHandCursor)
            detail_button.setVisible(False)
            if title == "Programı Güncelle":
                detail_button.clicked.connect(self.open_update_window)

            # Ensure button_container always reserves space, even when button is hidden
            button_layout.addWidget(detail_button)
            # Set a fixed height for the container equal to the button's size hint
            button_height = detail_button.sizeHint().height() + 10
            button_container.setFixedHeight(button_height)
            layout.addWidget(button_container)
            card.detail_button = detail_button
            card.setAttribute(Qt.WA_Hover, True)
            card.installEventFilter(self)

        card.setLayout(layout)
        return card

    def update_ciro_label(self, value):
        self.ciro_label.setText(f"{int(value):,}".replace(",", ".") + " TL")

    def update_navbar_selection(self, selected_button):
        pass

    def close(self):
        if self.parent() is not None:
            self.parent().show_main_page() 
        super().close()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            obj.setStyleSheet("""
                background-color: #e5e5ea;
                border-radius: 10px;
                padding: 30px 20px;
                margin: 5px;
            """)
            if hasattr(obj, "detail_button"):
                obj.detail_button.setVisible(True)
        elif event.type() == QtCore.QEvent.Leave:
            obj.setStyleSheet("""
                background-color: #ffffff;
                border-radius: 10px;
                padding: 30px 20px;
                margin: 5px;
            """)
            if hasattr(obj, "detail_button"):
                obj.detail_button.setVisible(False)
        return super().eventFilter(obj, event)

    def handle_back(self):
        self.close()

    def open_update_window(self):
        print("Güncelleme penceresi açılıyor...")
        from yonetim_paneli.update import UpdateWindow
        self.update_window = UpdateWindow()
        self.update_window.show()
        self.update_window.raise_()
        self.update_window.activateWindow()
        # self.hide()  # Geçici olarak yorum satırı yapıldı

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YonetimWindow()
    window.show()
    sys.exit(app.exec_())