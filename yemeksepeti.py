from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor

class ToggleSwitch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 24)  # Toggle yüksekliği sabit (24 piksel)
        self._checked = False
        self._circle_pos = 4  # Kapalı pozisyon

        # Animasyon
        self.animation = QPropertyAnimation(self, b"circle_pos", self)
        self.animation.setDuration(200)  # 200 ms animasyon süresi

    @pyqtProperty(int)
    def circle_pos(self):
        return self._circle_pos

    @circle_pos.setter
    def circle_pos(self, pos):
        self._circle_pos = pos
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Arka plan
        if self._checked:
            painter.setBrush(QColor("#cc0000"))  # Açıkken YemekSepeti kırmızısı
        else:
            painter.setBrush(QColor("#d3d3d3"))  # Kapalıyken gri
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 50, 24, 12, 12)

        # Yuvarlak top
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(self._circle_pos, 4, 16, 16)

    def mousePressEvent(self, event):
        self.toggle()

    def toggle(self):
        self._checked = not self._checked
        self.animation.setStartValue(self._circle_pos)
        if self._checked:
            self.animation.setEndValue(30)  # Açık pozisyon
        else:
            self.animation.setEndValue(4)   # Kapalı pozisyon
        self.animation.start()
        self.state_changed(self._checked)

    def state_changed(self, checked):
        if checked:
            print("Toggle açık!")
        else:
            print("Toggle kapalı!")

class YemekSepetiPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setStyleSheet("background-color: #f2f2f7;")
        self.setAutoFillBackground(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Navbar
        navbar_widget = QWidget()
        navbar_widget.setStyleSheet("background-color: #f2f2f7;")
        navbar_layout = QHBoxLayout(navbar_widget)
        navbar_layout.setContentsMargins(10, 5, 10, 5)
        navbar_layout.setSpacing(10)  # Öğeler arasında daha az boşluk

        back_wrapper = QWidget()
        back_wrapper.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QWidget:hover {
                background-color: transparent;
            }
        """)
        back_layout = QHBoxLayout(back_wrapper)
        back_layout.setSpacing(5)
        back_layout.setContentsMargins(0, 0, 0, 0)

        # Geri ikonu (sabit kırmızı renk)
        back_icon = QLabel()
        default_pixmap = QIcon("svg/back.svg").pixmap(20, 20)
        kirmizi_pixmap = QPixmap(20, 20)
        kirmizi_pixmap.fill(Qt.transparent)
        painter = QPainter(kirmizi_pixmap)
        painter.drawPixmap(0, 0, default_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(kirmizi_pixmap.rect(), QColor("#cc0000"))
        painter.end()
        back_icon.setPixmap(kirmizi_pixmap)
        back_icon.setFixedSize(20, 20)

        back_button = QPushButton("Geri")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #cc0000;  /* Sabit kırmızı renk */
            }
            QPushButton:hover {
                color: #cc0000;  /* Hover'da da aynı renk */
            }
        """)
        back_button.clicked.connect(self.go_back_to_main)

        back_layout.addWidget(back_icon)
        back_layout.addWidget(back_button)

        back_wrapper.setProperty("class", "back-wrapper")
        back_wrapper.setStyleSheet("""
            .back-wrapper:hover QPushButton {
                color: #cc0000;  /* Sabit kırmızı renk */
            }
        """)

        navbar_layout.addWidget(back_wrapper)

        logo_label = QLabel()
        logo_label.setFixedSize(30, 30)
        pixmap = QPixmap("yemeksepeti.png").scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setStyleSheet("background-color: transparent;")

        yemeksepeti_label = QLabel("YemekSepeti")
        yemeksepeti_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        logo_text_layout = QHBoxLayout()
        logo_text_layout.setSpacing(5)  # Logo ile başlık arasındaki boşluk azaltıldı
        logo_text_layout.addWidget(logo_label)
        logo_text_layout.addWidget(yemeksepeti_label)
        logo_text_layout.addStretch()

        navbar_layout.addLayout(logo_text_layout)

        # "Menu" öğesi
        menu_container = QWidget()
        menu_container.setStyleSheet("background-color: transparent;")  # Şeffaf arka plan
        menu_layout = QHBoxLayout(menu_container)
        menu_layout.setContentsMargins(10, 0, 10, 0)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_label = QLabel("Menu")
        menu_label.setStyleSheet("font-size: 14px; color: #333; background-color: transparent;")
        menu_layout.addWidget(menu_label)
        navbar_layout.addWidget(menu_container)

        # "Bölgeler" öğesi
        bolgeler_container = QWidget()
        bolgeler_container.setStyleSheet("background-color: transparent;")  # Şeffaf arka plan
        bolgeler_layout = QHBoxLayout(bolgeler_container)
        bolgeler_layout.setContentsMargins(10, 0, 10, 0)
        bolgeler_layout.setAlignment(Qt.AlignCenter)
        bolgeler_label = QLabel("Bölgeler")
        bolgeler_label.setStyleSheet("font-size: 14px; color: #333; background-color: transparent;")
        bolgeler_layout.addWidget(bolgeler_label)
        navbar_layout.addWidget(bolgeler_container)

        # "Ayarlar" öğesi
        ayarlar_container = QWidget()
        ayarlar_container.setStyleSheet("background-color: transparent;")  # Şeffaf arka plan
        ayarlar_layout = QHBoxLayout(ayarlar_container)
        ayarlar_layout.setContentsMargins(10, 0, 10, 0)
        ayarlar_layout.setAlignment(Qt.AlignCenter)
        ayarlar_label = QLabel("Ayarlar")
        ayarlar_label.setStyleSheet("font-size: 14px; color: #333; background-color: transparent;")
        ayarlar_layout.addWidget(ayarlar_label)
        navbar_layout.addWidget(ayarlar_container)

        # Toggle ve "Restoran" yazısını kapsayan bir widget
        toggle_container = QWidget()
        toggle_container.setFixedHeight(39)  # Yüksekliği 39 piksel
        toggle_container.setStyleSheet("""
            background-color: #ffffff;  /* Beyaz arka plan */
            border-radius: 15px;        /* Yuvarlak köşeler */
        """)
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(20, 0, 20, 0)  # Yatayda daha fazla boşluk
        toggle_layout.setSpacing(10)
        toggle_layout.setAlignment(Qt.AlignCenter)

        # "Restoran" yazısı
        restoran_label = QLabel("Restoran")
        restoran_label.setStyleSheet("font-size: 14px; color: #333; background-color: transparent;")
        toggle_layout.addWidget(restoran_label)

        # Toggle ekleme
        self.toggle_switch = ToggleSwitch()
        toggle_layout.addWidget(self.toggle_switch)

        navbar_layout.addWidget(toggle_container)

        navbar_widget.setFixedHeight(60)
        main_layout.addWidget(navbar_widget)

        # İçerik Alanı
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f2f2f7;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        title_label = QLabel("AKTİF SİPARİŞLER")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        content_layout.addWidget(title_label)

        # Güncellenmiş Kart Görünümü
        order_widget = QWidget()
        order_widget.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        order_layout = QHBoxLayout(order_widget)
        order_layout.setContentsMargins(15, 15, 15, 15)
        order_layout.setSpacing(20)

        # Müşteri Bilgisi (Sol taraf)
        customer_widget = QWidget()
        customer_layout = QHBoxLayout(customer_widget)
        customer_layout.setSpacing(10)
        customer_layout.setAlignment(Qt.AlignCenter)

        # Müşteri ikonu
        customer_icon = QLabel()
        customer_icon.setFixedSize(40, 40)
        customer_icon.setStyleSheet("""
            background-color: #34c759;
            border-radius: 20px;
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
        """)
        customer_icon.setAlignment(Qt.AlignCenter)
        customer_icon.setText("D")  # İlk harf (örneğin "Davut Dalmiş" için "D")
        customer_layout.addWidget(customer_icon)

        # Müşteri adı ve kod
        customer_info_layout = QVBoxLayout()
        customer_info_layout.setSpacing(5)
        customer_info_layout.setAlignment(Qt.AlignCenter)
        customer_name = QLabel("Davut Dalmiş")
        customer_name.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        customer_name.setAlignment(Qt.AlignCenter)
        customer_code = QLabel("ys123")
        customer_code.setStyleSheet("font-size: 12px; color: #666;")
        customer_code.setAlignment(Qt.AlignCenter)
        customer_info_layout.addWidget(customer_name)
        customer_info_layout.addWidget(customer_code)
        customer_layout.addLayout(customer_info_layout)

        order_layout.addWidget(customer_widget, stretch=1)

        # Dikey Çubuk 1
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet("background-color: #d3d3d3; max-width: 1px;")
        order_layout.addWidget(separator1)

        # Ödeme Bilgisi
        payment_widget = QWidget()
        payment_layout = QVBoxLayout(payment_widget)
        payment_layout.setSpacing(5)
        payment_layout.setAlignment(Qt.AlignCenter)
        payment_method = QLabel("Online Ödeme")
        payment_method.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        payment_method.setAlignment(Qt.AlignCenter)
        payment_amount = QLabel("₺320,00")
        payment_amount.setStyleSheet("font-size: 12px; color: #666;")
        payment_amount.setAlignment(Qt.AlignCenter)
        payment_layout.addWidget(payment_method)
        payment_layout.addWidget(payment_amount)
        order_layout.addWidget(payment_widget, stretch=1)

        # Dikey Çubuk 2
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #d3d3d3; max-width: 1px;")
        order_layout.addWidget(separator2)

        # Sipariş Zamanı
        time_widget = QWidget()
        time_layout = QVBoxLayout(time_widget)
        time_layout.setSpacing(5)
        time_layout.setAlignment(Qt.AlignCenter)
        order_time = QLabel("12:15")
        order_time.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        order_time.setAlignment(Qt.AlignCenter)
        total_time = QLabel("Toplam Süre: 3dk 45sn")
        total_time.setStyleSheet("font-size: 12px; color: #666;")
        total_time.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(order_time)
        time_layout.addWidget(total_time)
        order_layout.addWidget(time_widget, stretch=1)

        # Dikey Çubuk 3
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.VLine)
        separator3.setFrameShadow(QFrame.Sunken)
        separator3.setStyleSheet("background-color: #d3d3d3; max-width: 1px;")
        order_layout.addWidget(separator3)

        # Durum
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        status_layout.setAlignment(Qt.AlignCenter)
        status_label = QLabel("Hazırlanıyor")
        status_label.setStyleSheet("font-size: 14px; color: #666;")
        status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(status_label)
        order_layout.addWidget(status_widget, stretch=1)

        # Dikey Çubuk 4
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.VLine)
        separator4.setFrameShadow(QFrame.Sunken)
        separator4.setStyleSheet("background-color: #d3d3d3; max-width: 1px;")
        order_layout.addWidget(separator4)

        # Butonlar (Sağ taraf)
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignCenter)

        # Yola Çıkar Butonu
        start_button = QPushButton("Yola Çıkar")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #cc0000;  /* YemekSepeti kırmızısı */
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #b30000;  /* Hover'da daha koyu kırmızı */
            }
        """)
        start_button.setFixedWidth(100)
        buttons_layout.addWidget(start_button)

        # İptal Butonu
        cancel_button = QPushButton("X")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ffebee;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                color: #e57373;
            }
            QPushButton:hover {
                background-color: #ffcdd2;
            }
        """)
        cancel_button.setFixedWidth(40)
        buttons_layout.addWidget(cancel_button)

        order_layout.addWidget(buttons_widget, stretch=1)

        content_layout.addWidget(order_widget)
        content_layout.addStretch()

        main_layout.addWidget(content_widget)

    def go_back_to_main(self):
        self.parent.show_main_page()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = YemekSepetiPage()
    window.show()
    sys.exit(app.exec_())