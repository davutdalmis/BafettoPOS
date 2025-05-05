
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtMultimedia import QSound
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Firestore bağlantısını bağımsız olarak başlat
try:
    cred = credentials.Certificate("firebase/firebase-adminsdk.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Firestore bağlantısı kurulamadı: {e}")
    db = None
from datetime import datetime, timezone
from firebase_admin import firestore

class TimerCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.elapsed_seconds = 0
        self.setFixedSize(60, 60)

    def update_time(self, elapsed_seconds):
        self.elapsed_seconds = elapsed_seconds
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(6, 6, -6, -6)
        pen = painter.pen()
        pen.setWidth(3)

        if self.elapsed_seconds < 60:
            pen.setColor(QColor("#34c759"))
        elif self.elapsed_seconds < 300:
            pen.setColor(QColor("#ffcc00"))
        else:
            pen.setColor(QColor("#ff3b30"))

        painter.setPen(pen)
        painter.drawEllipse(rect)

        painter.setPen(Qt.black)
        painter.drawText(self.rect(), Qt.AlignCenter, self.get_display_text())

    def get_display_text(self):
        if self.elapsed_seconds < 60:
            return f"{self.elapsed_seconds} SN"
        elif self.elapsed_seconds < 3600:
            minutes = self.elapsed_seconds // 60
            return f"{minutes} DK"
        elif self.elapsed_seconds < 86400:
            hours = self.elapsed_seconds // 3600
            return f"{hours} SA"
        else:
            days = self.elapsed_seconds // 86400
            return f"{days} GÜN"

class ToggleSwitch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 24)
        self._checked = False
        self._circle_pos = 4

        self.animation = QPropertyAnimation(self, b"circle_pos", self)
        self.animation.setDuration(200)

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

        if self._checked:
            painter.setBrush(QColor("#b00020"))
        else:
            painter.setBrush(QColor("#d3d3d3"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 50, 24, 12, 12)

        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(self._circle_pos, 4, 16, 16)

    def mousePressEvent(self, event):
        self.toggle()

    def toggle(self):
        self._checked = not self._checked
        self.animation.setStartValue(self._circle_pos)
        if self._checked:
            self.animation.setEndValue(30)
        else:
            self.animation.setEndValue(4)
        self.animation.start()
        self.state_changed(self._checked)

    def state_changed(self, checked):
        pass  # Debug print removed

def get_active_orders():
    if db is None:
        print("Firestore bağlantısı yok, siparişler çekilemedi.")
        return []
    try:
        active_statuses = ["Onay Bekleyen Sipariş", "Onaylandı", "Hazırlanıyor", "Hazır", "Yolda"]
        orders_ref = db.collection('siparisler').where(
            filter=firestore.FieldFilter('siparisDurumu', 'in', active_statuses)
        )
        orders = orders_ref.stream()
        active_orders = []
        for order in orders:
            order_data = order.to_dict()
            order_data['id'] = order.id
            # Tag platform for these orders
            order_data['platform'] = 'getiryemek'
            siparis_tarihi = order_data.get('siparisTarihi')
            if siparis_tarihi and order_data.get('siparisDurumu') == "Onay Bekleyen Sipariş":
                try:
                    siparis_datetime = siparis_tarihi
                    current_datetime = datetime.now(timezone.utc)
                    time_diff = (current_datetime - siparis_datetime).total_seconds()
                    if time_diff > 3600:
                        update_order_status(order.id, "İptal")
                        continue
                except Exception as e:
                    pass  # Debug print removed
            active_orders.append(order_data)
        return active_orders
    except Exception as e:
        print(f"Siparişler çekilirken hata: {e}")
        return []

def update_order_status(order_id, new_status):
    if db is None:
        print("Firestore bağlantısı yok, durum güncellenemedi.")
        return
    try:
        db.collection('siparisler').document(order_id).update({
            'siparisDurumu': new_status,
            'guncellenmeTarihi': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"Durum güncellenirken hata: {e}")

def get_user_display_name(user_id):
    if db is None:
        print("Firestore bağlantısı yok, kullanıcı adı alınamadı.")
        return "Bilinmeyen Müşteri"
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            display_name = user_data.get('displayName', "Bilinmeyen Müşteri")
            return display_name
        return "Bilinmeyen Müşteri"
    except Exception as e:
        print(f"Kullanıcı bilgileri alınırken hata: {e}")
        return "Bilinmeyen Müşteri"

class OrderCard(QWidget):
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        siparis_tarihi = self.order_data.get('siparisTarihi')
        if siparis_tarihi:
            now = datetime.now(timezone.utc)
            self.elapsed_seconds = int((now - siparis_tarihi).total_seconds())
        else:
            self.elapsed_seconds = 0
        self.timer = QTimer(self)
        self.flash_timer = QTimer(self)
        self.flash_counter = 0
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#ffffff"))
        self.setPalette(palette)
        self.setStyleSheet("background-color: #ffffff; border-radius: 10px; margin: 10px; padding: 15px 20px;")
        self.setup_ui()
        self.setup_timers()
        # Debug print removed

    def setup_ui(self):
        self.order_id = self.order_data['id']
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        info_layout = QVBoxLayout()
        order_number = QLabel(f"bf{self.order_id[-3:]}")
        order_number.setStyleSheet("background-color: transparent; color: #333333; font-weight: bold; font-size: 16px;")
        user_id = self.order_data.get('kullaniciId', 'Müşteri')
        display_name = get_user_display_name(user_id)
        order_detail = QLabel(f"{len(self.order_data.get('urunler', []))} ürün, {display_name}")
        order_detail.setStyleSheet("background-color: transparent; color: #666666; font-size: 12px;")
        info_layout.addWidget(order_number)
        info_layout.addWidget(order_detail)

        self.time_circle = TimerCircle()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        layout.addLayout(info_layout)
        layout.addWidget(self.time_circle)

    def update_timer(self):
        self.elapsed_seconds += 1
        self.time_circle.update_time(self.elapsed_seconds)

    def setup_timers(self):
        if self.order_data.get('siparisDurumu') == "Onay Bekleyen Sipariş":
            self.flash_timer.timeout.connect(self.flash_background)
            self.flash_timer.start(500)
            QTimer.singleShot(5000, self.stop_flash)

    def flash_background(self):
        if self.flash_counter >= 10:
            self.stop_flash()
        else:
            if self.flash_counter % 2 == 0:
                self.setStyleSheet("background-color: #ffe6e6; border-radius: 10px; margin: 10px; padding: 15px 20px;")
            else:
                self.setStyleSheet("background-color: #ffffff; border-radius: 10px; margin: 10px; padding: 15px 20px;")
            self.flash_counter += 1

    def stop_flash(self):
        self.flash_timer.stop()
        self.setStyleSheet("background-color: #ffffff; border-radius: 10px; margin: 10px; padding: 15px 20px;")

    def stop_timers(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.flash_timer.isActive():
            self.flash_timer.stop()

    def update_order(self, new_order_data):
        self.order_data = new_order_data
        # Update order number and user name
        order_number_label = self.findChild(QLabel)
        if order_number_label:
            order_number_label.setText(f"bf{self.order_data['id'][-3:]}")
        user_id = self.order_data.get('kullaniciId', 'Müşteri')
        display_name = get_user_display_name(user_id)
        order_detail_label = self.findChildren(QLabel)[1] if len(self.findChildren(QLabel)) > 1 else None
        if order_detail_label:
            order_detail_label.setText(f"{len(self.order_data.get('urunler', []))} ürün, {display_name}")

        # Update elapsed time based on new order data
        siparis_tarihi = self.order_data.get('siparisTarihi')
        if siparis_tarihi:
            now = datetime.now(timezone.utc)
            self.elapsed_seconds = int((now - siparis_tarihi).total_seconds())
            self.time_circle.update_time(self.elapsed_seconds)

        # Manage flash timer if needed
        if self.order_data.get('siparisDurumu') != "Onay Bekleyen Sipariş":
            self.stop_flash()

class BafettoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.order_cards = {}
        self.active_order_card = None
        self.previous_order_count = 0
        self.progress_widgets = []  # Progress bar widget'larını saklamak için

        self.setStyleSheet("background-color: #f2f2f7;")
        self.setAutoFillBackground(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # NAVBAR (fixed, outside scroll area)
        navbar_widget = QWidget()
        navbar_widget.setStyleSheet("background-color: #f2f2f7;")
        navbar_layout = QHBoxLayout(navbar_widget)
        navbar_layout.setContentsMargins(0, 0, 0, 0)
        navbar_layout.setSpacing(10)

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

        back_icon = QLabel()
        default_pixmap = QIcon("svg/back.svg").pixmap(20, 20)
        mor_pixmap = QPixmap(20, 20)
        mor_pixmap.fill(Qt.transparent)
        painter = QPainter(mor_pixmap)
        painter.drawPixmap(0, 0, default_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(mor_pixmap.rect(), QColor("#ff3b30"))
        painter.end()
        back_icon.setPixmap(mor_pixmap)
        back_icon.setFixedSize(20, 20)

        back_button = QPushButton("Geri")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #ff3b30;
            }
            QPushButton:hover {
                color: #ff3b30;
            }
        """)
        back_button.clicked.connect(self.go_back_to_main)

        back_layout.addWidget(back_icon)
        back_layout.addWidget(back_button)

        back_wrapper.setProperty("class", "back-wrapper")
        back_wrapper.setStyleSheet("""
            .back-wrapper:hover QPushButton {
                color: #ff3b30;
            }
        """)

        navbar_layout.addWidget(back_wrapper)

        logo_label = QLabel()
        pixmap = QPixmap("bafetto.png")
        logo_label.setPixmap(pixmap)
        logo_label.setScaledContents(True)
        logo_label.setFixedSize(30, 30)
        logo_label.setStyleSheet("background-color: transparent;")

        getiryemek_label = QLabel("Bafetto")
        getiryemek_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        logo_text_layout = QHBoxLayout()
        logo_text_layout.setSpacing(5)
        logo_text_layout.addWidget(logo_label)
        logo_text_layout.addWidget(getiryemek_label)
        logo_text_layout.addStretch()

        navbar_layout.addLayout(logo_text_layout)

        menu_container = QWidget()
        menu_container.setStyleSheet("background-color: transparent;")
        menu_layout = QHBoxLayout(menu_container)
        menu_layout.setContentsMargins(10, 0, 10, 0)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_label = QLabel("Menu")
        menu_label.setStyleSheet("font-size: 14px; color: #333; background-color: transparent;")
        menu_layout.addWidget(menu_label)
        navbar_layout.addWidget(menu_container)

        bolgeler_container = QWidget()
        bolgeler_container.setStyleSheet("background-color: transparent;")
        bolgeler_layout = QHBoxLayout(bolgeler_container)
        bolgeler_layout.setContentsMargins(10, 0, 10, 0)
        bolgeler_layout.setAlignment(Qt.AlignCenter)
        bolgeler_label = QLabel("Bölgeler")
        bolgeler_label.setStyleSheet("font-size: 14px; color: #333; background-color: transparent;")
        bolgeler_layout.addWidget(bolgeler_label)
        navbar_layout.addWidget(bolgeler_container)

        ayarlar_container = QWidget()
        ayarlar_container.setStyleSheet("background-color: transparent;")
        ayarlar_layout = QHBoxLayout(ayarlar_container)
        ayarlar_layout.setContentsMargins(10, 0, 10, 0)
        ayarlar_layout.setAlignment(Qt.AlignCenter)
        ayarlar_label = QLabel("Ayarlar")
        ayarlar_label.setStyleSheet("font-size: 14px; color: #333; background-color: transparent;")
        ayarlar_layout.addWidget(ayarlar_label)
        navbar_layout.addWidget(ayarlar_container)

        toggle_container = QWidget()
        toggle_container.setFixedHeight(39)
        toggle_container.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 15px;
        """)
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(20, 0, 20, 0)
        toggle_layout.setSpacing(10)
        toggle_layout.setAlignment(Qt.AlignCenter)

        restoran_label = QLabel("Restoran")
        restoran_label.setStyleSheet("font-size: 14px; color: #333; background-color: transparent;")
        toggle_layout.addWidget(restoran_label)

        self.toggle_switch = ToggleSwitch()
        toggle_layout.addWidget(self.toggle_switch)

        navbar_layout.addWidget(toggle_container)

        navbar_widget.setFixedHeight(60)

        # MAIN BODY LAYOUT: sidebar and scroll area
        main_body_layout = QHBoxLayout()
        main_body_layout.setContentsMargins(0, 0, 0, 0)
        main_body_layout.setSpacing(0)

        # --- SIDEBAR (fixed) ---
        sidebar_content = QWidget()
        sidebar_content.setMinimumWidth(320)
        sidebar_content.setMaximumWidth(320)
        sidebar_content.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.sidebar_layout = QVBoxLayout(sidebar_content)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 20)  # Add 20px bottom margin
        self.sidebar_layout.setSpacing(0)

        hazirlaniyor_label = QLabel("Bekleyen Siparişler")
        hazirlaniyor_label.setStyleSheet("color: #333333; font-size: 16px; font-weight: bold; margin: 20px;")
        self.sidebar_layout.addWidget(hazirlaniyor_label)
        self.sidebar_layout.addStretch()

        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sidebar_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #f7f7f7;
                border: none;
            }
            QScrollBar:vertical {
                width: 0px;
                background: transparent;
            }
            QScrollBar:horizontal {
                height: 0px;
                background: transparent;
            }
        """)
        sidebar_scroll.setWidget(sidebar_content)
        sidebar_scroll.setFixedWidth(320)

        # --- PAGE CONTENT (scrollable) ---
        # Instead of putting navbar/sidebar in scroll, only content area is scrollable
        # Create a widget to hold the page content (formerly content_widget_container)
        scroll_content_widget = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content_widget)
        scroll_content_layout.setContentsMargins(0, 0, 0, 20)
        scroll_content_layout.setSpacing(0)

        # Create the page_layout (as before) inside scroll_content_widget
        page_layout = QHBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)
        scroll_content_layout.addLayout(page_layout)

        # --- left: (empty placeholder, sidebar is outside scroll) ---
        # --- right: main content area ---
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f2f2f7;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        title_label = QLabel("AKTİF SİPARİŞLER")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        content_layout.addWidget(title_label)

        self.progress_widget = QWidget()
        self.progress_widget.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        self.progress_layout = QHBoxLayout(self.progress_widget)
        self.progress_layout.setContentsMargins(20, 20, 20, 20)
        self.progress_layout.setSpacing(40)
        content_layout.addWidget(self.progress_widget)

        order_info_header = QWidget()
        order_info_header_layout = QHBoxLayout(order_info_header)
        order_info_header_layout.setContentsMargins(0, 0, 0, 0)
        order_info_header_layout.setSpacing(10)

        order_info_title = QLabel("SİPARİŞ BİLGİLERİ")
        order_info_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        order_info_header_layout.addWidget(order_info_title)
        order_info_header_layout.addStretch()
        adisyon_button = QPushButton("Adisyon Çıkart")
        adisyon_button.setFixedHeight(32)
        adisyon_button.setStyleSheet("""
            QPushButton {
                background-color: #ff3b30;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #ff5e57;
            }
        """)
        order_info_header_layout.addWidget(adisyon_button)
        content_layout.addWidget(order_info_header)

        self.order_info_card = QWidget()
        self.order_info_card.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        order_info_layout = QVBoxLayout(self.order_info_card)
        order_info_layout.setContentsMargins(20, 20, 20, 20)
        order_info_layout.setSpacing(15)

        top_info_layout = QHBoxLayout()
        top_info_layout.setAlignment(Qt.AlignLeft)

        customer_grid = QWidget()
        grid_layout = QGridLayout(customer_grid)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(30)
        grid_layout.setVerticalSpacing(10)

        self.info_labels = {}
        info_pairs = [
            ("Müşteri İsmi", "customer_name_label", ""),
            ("Sipariş No.", "order_no_label", ""),
            ("Sokak", "street_label", ""),
            ("Bina No.", "building_no_label", ""),
            ("Kat", "floor_label", ""),
            ("Daire No.", "apartment_no_label", ""),
            ("Adres Açıklaması", "description_label", ""),
            ("Ödeme Yöntemi", "payment_method_label", ""),
        ]

        for row, (label_text, object_name, value_text) in enumerate(info_pairs):
            label = QLabel(label_text)
            label.setStyleSheet("color: #8e8e93; font-size: 12px; font-weight: 500; margin-bottom: 2px;")
            value = QLabel(value_text)
            value.setObjectName(object_name)
            if label_text == "Ödeme Yöntemi":
                value.setStyleSheet("color: #57007f; font-size: 16px; font-weight: 700; margin-top: 2px;")
            else:
                value.setStyleSheet("color: #000000; font-size: 16px; font-weight: 600; margin-top: 2px;")
            self.info_labels[object_name] = value
            grid_layout.addWidget(label, row, 0, Qt.AlignRight)
            grid_layout.addWidget(value, row, 1, Qt.AlignLeft)

        top_info_layout.addWidget(customer_grid, alignment=Qt.AlignLeft)

        order_summary_widget = QWidget()
        order_summary_widget.setFixedWidth(520)
        order_summary_widget.setStyleSheet("background-color: #ffffff; border-radius: 0px;")
        order_summary_layout = QVBoxLayout(order_summary_widget)
        order_summary_layout.setContentsMargins(10, 0, 10, 10)
        order_summary_layout.setSpacing(0)

        self.order_summary_grid = QGridLayout()
        self.order_summary_grid.setContentsMargins(0, 0, 0, 0)
        self.order_summary_grid.setSpacing(0)

        def create_table_label(text, bold=False):
            label = QLabel(text)
            style = """
                background-color: #e0e0e5;
                border: 1px solid #d3d3d3;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                color: #333333;
            """ if bold else """
                background-color: #f2f2f7;
                border: 1px solid #d3d3d3;
                padding: 8px;
                font-size: 14px;
                color: #666666;
            """
            label.setStyleSheet(style)
            return label

        self.order_summary_grid.addWidget(create_table_label("Ürün", bold=True), 0, 0)
        self.order_summary_grid.addWidget(create_table_label("Adet", bold=True), 0, 1)
        self.order_summary_grid.addWidget(create_table_label("Tutar", bold=True), 0, 2)

        order_summary_layout.addLayout(self.order_summary_grid)
        order_summary_layout.addStretch()

        self.total_widget = QWidget()
        total_layout = QHBoxLayout(self.total_widget)
        total_layout.setContentsMargins(0, 10, 0, 0)
        total_layout.setSpacing(5)
        total_label = QLabel("Toplam:")
        total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        self.total_amount = QLabel("")
        self.total_amount.setStyleSheet("font-size: 16px; font-weight: bold; color: #34c759;")
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_amount)
        order_summary_layout.addWidget(self.total_widget)

        top_info_layout.addWidget(order_summary_widget, alignment=Qt.AlignTop)
        order_info_layout.addLayout(top_info_layout)

        actions_widget = QWidget()
        self.actions_layout = QHBoxLayout(actions_widget)
        self.actions_layout.setContentsMargins(0, 20, 0, 0)
        self.actions_layout.setSpacing(10)

        self.cancel_button = QPushButton("İptal Et")
        self.cancel_button.setFixedHeight(36)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ff3b30;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff5e57;
            }
        """)
        self.actions_layout.addWidget(self.cancel_button, alignment=Qt.AlignLeft)
        self.actions_layout.addStretch()
        self.ready_button = QPushButton("Sipariş Hazırlandı")
        self.ready_button.setFixedHeight(36)
        self.ready_button.setStyleSheet("""
            QPushButton {
                background-color: #34c759;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5cd17b;
            }
        """)
        self.actions_layout.addWidget(self.ready_button, alignment=Qt.AlignRight)
        order_info_layout.addWidget(actions_widget)
        content_layout.addWidget(self.order_info_card)
        content_layout.addStretch()
        page_layout.addWidget(content_widget)

        # --- MAIN SCROLL AREA for page content only ---
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #f2f2f7;
                border: none;
            }
            QScrollBar:vertical {
                width: 0px;
                background: transparent;
            }
            QScrollBar:horizontal {
                height: 0px;
                background: transparent;
            }
        """)
        main_scroll.setWidget(scroll_content_widget)

        # Add sidebar and main_scroll to main_body_layout
        main_body_layout.addWidget(sidebar_scroll)
        main_body_layout.addWidget(main_scroll)

        # Add navbar and main_body_layout to main_layout
        main_layout.addWidget(navbar_widget)
        main_layout.addLayout(main_body_layout)

        print("GetirYemek arayüzü başlatılıyor...")
        self.load_orders()
        self.listen_to_orders()

    def go_back_to_main(self):
        print("Ana sayfaya geri dönülüyor.")
        self.parent.show_main_page()

    def update_progress_bar(self, order_data):
        # Mevcut progress bar widget'larını temizle
        for item in self.progress_widgets:
            self.progress_layout.removeWidget(item)
            item.deleteLater()
        self.progress_widgets = []

        status = order_data.get('siparisDurumu', 'Bilinmeyen')
        siparis_tarihi = order_data.get('siparisTarihi')
        guncellenme_tarihi = order_data.get('guncellenmeTarihi')

        # Zaman damgalarını formatla
        def format_timestamp(timestamp):
            if timestamp:
                try:
                    return timestamp.strftime("%H:%M")
                except (AttributeError, ValueError, TypeError):
                    return ""
            return ""

        # Adım tanımları
        steps = [
            ("Sipariş Onaylandı", "svg/list.svg", False, ""),
            ("Sipariş Kabul Edildi", "svg/approve.svg", False, ""),
            ("Sipariş Hazırlanıp Yola Çıktı", "svg/ready.svg", False, ""),
            ("Teslim Edildi", "svg/delivered.svg", False, "")
        ]

        # Duruma göre adımları işaretle
        if status in ["Onay Bekleyen Sipariş", "Onaylandı"]:
            steps[0] = ("Sipariş Onaylandı", "svg/list.svg", True, format_timestamp(siparis_tarihi))
        elif status == "Hazırlanıyor":
            steps[0] = ("Sipariş Onaylandı", "svg/list.svg", True, format_timestamp(siparis_tarihi))
            steps[1] = ("Sipariş Kabul Edildi", "svg/approve.svg", True, format_timestamp(guncellenme_tarihi))
        elif status in ["Hazır", "Yolda"]:
            steps[0] = ("Sipariş Onaylandı", "svg/list.svg", True, format_timestamp(siparis_tarihi))
            steps[1] = ("Sipariş Kabul Edildi", "svg/approve.svg", True, format_timestamp(guncellenme_tarihi))
            steps[2] = ("Sipariş Hazırlanıp Yola Çıktı", "svg/ready.svg", True, format_timestamp(guncellenme_tarihi))
        elif status == "Teslim Edildi":
            steps[0] = ("Sipariş Onaylandı", "svg/list.svg", True, format_timestamp(siparis_tarihi))
            steps[1] = ("Sipariş Kabul Edildi", "svg/approve.svg", True, format_timestamp(guncellenme_tarihi))
            steps[2] = ("Sipariş Hazırlanıp Yola Çıktı", "svg/ready.svg", True, format_timestamp(guncellenme_tarihi))
            steps[3] = ("Teslim Edildi", "svg/delivered.svg", True, format_timestamp(guncellenme_tarihi))

        # Progress bar'ı yeniden oluştur
        for index, (step_name, icon_path, active, time_text) in enumerate(steps):
            step_container = QWidget()
            step_layout = QVBoxLayout(step_container)
            step_layout.setAlignment(Qt.AlignCenter)
            step_layout.setContentsMargins(0, 0, 0, 0)

            # Wrap QSvgWidget in a container QWidget for padding and background
            icon_container = QWidget()
            icon_container.setFixedSize(44, 44)
            icon_container.setStyleSheet(
                f"background-color: {'#b00020' if active else '#d3d3d3'}; border-radius: 22px; padding: 4px;"
            )
            icon_widget = QSvgWidget(icon_path, icon_container)
            icon_widget.setFixedSize(32, 32)
            icon_widget.move(6, 6)  # optional fine tuning

            text_label = QLabel(step_name)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet("color: #333333; font-weight: bold;" if active else "color: #999999;")

            time_label = QLabel(time_text)
            time_label.setAlignment(Qt.AlignCenter)
            time_label.setStyleSheet("color: #333333; font-weight: bold;" if active else "color: #999999;")

            step_layout.addWidget(icon_container)
            step_layout.addWidget(text_label)
            step_layout.addWidget(time_label)

            self.progress_layout.addWidget(step_container)
            self.progress_widgets.append(step_container)

            if index < len(steps) - 1:
                progress_line = QFrame()
                progress_line.setFixedHeight(4)
                progress_line.setFixedWidth(60)
                progress_line.setStyleSheet(f"background-color: {'#b00020' if active else '#d3d3d3'}; border: none;")
                self.progress_layout.addWidget(progress_line)
                self.progress_widgets.append(progress_line)

    def load_orders(self):
        orders = get_active_orders()
        # Notification logic for new "Onay Bekleyen Sipariş"
        current_order_count = len([o for o in orders if o.get('siparisDurumu') == "Onay Bekleyen Sipariş"])
        if current_order_count > self.previous_order_count:
            try:
                sound_file = "notification.wav"
                if os.path.exists(sound_file):
                    QSound.play(sound_file)
            except Exception as e:
                print(f"Bildirim sesi çalınırken hata: {e}")
        self.previous_order_count = current_order_count

        print(f"Aktif siparişler: {[o['id'] for o in orders]}")
        if self.active_order_card:
            print(f"Seçili kart: {self.active_order_card.order_data['id']}")
        current_order_ids = {order['id'] for order in orders}

        # Remove OrderCard widgets that are no longer present, but leave the stretch
        current_widgets = [self.sidebar_layout.itemAt(i).widget() for i in range(self.sidebar_layout.count())]
        for widget in current_widgets:
            if isinstance(widget, OrderCard) and widget.order_data['id'] not in current_order_ids:
                self.sidebar_layout.removeWidget(widget)
                widget.stop_timers()
                widget.deleteLater()
                if self.active_order_card == widget:
                    self.active_order_card = None
                    self.clear_order_info()
                del self.order_cards[widget.order_data['id']]

        orders.sort(key=lambda x: x.get('siparisTarihi') if x.get('siparisTarihi') else datetime.min, reverse=True)

        for index, order in enumerate(orders):
            order_id = order['id']
            if order_id not in self.order_cards:
                order_card = OrderCard(order, parent=self)
                order_card.mousePressEvent = lambda event, card=order_card, o=order: self.select_order_card(card, o)
                self.order_cards[order_id] = order_card
                self.sidebar_layout.insertWidget(1, order_card)
            else:
                existing_card = self.order_cards[order_id]
                existing_card.update_order(order)
                current_index = self.sidebar_layout.indexOf(existing_card)
                if current_index != index + 1:
                    self.sidebar_layout.removeWidget(existing_card)
                    self.sidebar_layout.insertWidget(1 + index, existing_card)

        # Seçili kartın detay bilgisini güncelle
        if self.active_order_card:
            active_id = self.active_order_card.order_data['id']
            for order in orders:
                if order['id'] == active_id:
                    self.update_order_info(order)
                    self.update_progress_bar(order)
                    self.setup_buttons(order)
                    break

        if not orders and self.sidebar_layout.count() == 2:
            no_order_label = QLabel("Aktif sipariş bulunmamaktadır.")
            no_order_label.setStyleSheet("font-size: 14px; color: #666;")
            self.sidebar_layout.insertWidget(1, no_order_label)
            self.clear_progress_bar()

        if orders and not self.active_order_card:
            self.select_order_card(list(self.order_cards.values())[0], orders[0])

    def clear_progress_bar(self):
        print("Progress bar temizleniyor...")
        for item in self.progress_widgets:
            self.progress_layout.removeWidget(item)
            item.deleteLater()
        self.progress_widgets = []

    def listen_to_orders(self):
        if db is None:
            print("Firestore bağlantısı yok, gerçek zamanlı dinleme başlatılamıyor.")
            return
        def on_snapshot(col_snapshot, changes, read_time):
            print("Firestore'dan güncelleme alındı, siparişler yeniden yükleniyor.")
            QTimer.singleShot(0, self.load_orders)
        try:
            print("Gerçek zamanlı dinleme başlatılıyor...")
            db.collection('siparisler').where(
                filter=firestore.FieldFilter(
                    'siparisDurumu', 'in', ["Onay Bekleyen Sipariş", "Onaylandı", "Hazırlanıyor", "Hazır", "Yolda"]
                )
            ).on_snapshot(on_snapshot)
            print("Dinleme başarıyla başlatıldı.")
        except Exception as e:
            print(f"Gerçek zamanlı dinleme başlatılırken hata: {e}")

    def select_order_card(self, selected_card, order_data):
        if self.active_order_card:
            self.active_order_card.setStyleSheet("background-color: #ffffff; border-radius: 10px; margin: 10px; padding: 15px 20px;")
        selected_card.setStyleSheet("background-color: #ffe6e6; border-radius: 10px; margin: 10px; padding: 15px 20px;")
        self.active_order_card = selected_card
        self.update_order_info(order_data)
        self.setup_buttons(order_data)
        self.update_progress_bar(order_data)

    def update_order_info(self, order_data):
        user_id = order_data.get('kullaniciId', 'Müşteri')
        display_name = get_user_display_name(user_id)
        teslimat_adresi = order_data.get('teslimatAdresi', {})
        self.info_labels["customer_name_label"].setText(display_name)
        self.info_labels["order_no_label"].setText(f"bf{order_data['id'][-3:]}")
        self.info_labels["street_label"].setText(teslimat_adresi.get('street', 'Bilinmiyor'))
        self.info_labels["building_no_label"].setText(teslimat_adresi.get('buildingNo', 'Bilinmiyor'))
        self.info_labels["floor_label"].setText(teslimat_adresi.get('floor', 'Bilinmiyor'))
        self.info_labels["apartment_no_label"].setText(teslimat_adresi.get('apartmentNo', 'Bilinmiyor'))
        self.info_labels["description_label"].setText(teslimat_adresi.get('description', 'Bilinmiyor'))
        odeme_yontemi = order_data.get('odemeYontemi', 'Bilinmeyen')
        if odeme_yontemi == 'credit-card':
            odeme_detaylari = order_data.get('odemeDetaylari', {})
            kart_turu = odeme_detaylari.get('kartTuru', 'Kredi Kartı')
            self.info_labels["payment_method_label"].setText(f"Kredi Kartı ({kart_turu})")
        elif odeme_yontemi == 'food-card':
            odeme_detaylari = order_data.get('odemeDetaylari', {})
            yemek_karti_turu = odeme_detaylari.get('yemekKartiTuru', 'Yemek Kartı')
            self.info_labels["payment_method_label"].setText(f"Yemek Kartı ({yemek_karti_turu})")
        else:
            self.info_labels["payment_method_label"].setText(odeme_yontemi.replace('-', ' ').title())

        rows = self.order_summary_grid.rowCount()
        for row in range(1, rows):
            for col in range(3):
                item = self.order_summary_grid.itemAtPosition(row, col)
                if item and item.widget():
                    widget = item.widget()
                    self.order_summary_grid.removeWidget(widget)
                    widget.deleteLater()

        products = order_data.get('urunler', [])
        for row, product in enumerate(products, 1):
            extras = product.get('extras', [])
            urun_adi = product.get('urunAdi', 'Bilinmeyen Ürün')
            if extras and isinstance(extras, list):
                extras_str = ', '.join([extra.get('name', '') for extra in extras if extra.get('name')])
                urun_adi += f" ({extras_str})" if extras_str else ""
            self.order_summary_grid.addWidget(self.create_table_label(urun_adi), row, 0)
            self.order_summary_grid.addWidget(self.create_table_label(str(product.get('miktar', 1))), row, 1)
            self.order_summary_grid.addWidget(self.create_table_label(f"{product.get('fiyat', 0):.2f}₺"), row, 2)

        self.total_amount.setText(f"{order_data.get('toplamTutar', 0):.2f}₺")

    def create_table_label(self, text, bold=False):
        label = QLabel(text)
        style = """
            background-color: #e0e0e5;
            border: 1px solid #d3d3d3;
            padding: 8px;
            font-weight: bold;
            font-size: 14px;
            color: #333333;
        """ if bold else """
            background-color: #f2f2f7;
            border: 1px solid #d3d3d3;
            padding: 8px;
            font-size: 14px;
            color: #666666;
        """
        label.setStyleSheet(style)
        return label

    def setup_buttons(self, order_data):
        status = order_data.get('siparisDurumu', 'Bilinmeyen')
        order_id = order_data['id']

        for i in reversed(range(self.actions_layout.count())):
            widget = self.actions_layout.itemAt(i).widget()
            if widget and widget in (self.cancel_button, self.ready_button):
                self.actions_layout.removeWidget(widget)
                widget.deleteLater()

        def create_action_button(text, next_status, bg_color, hover_color):
            button = QPushButton(text)
            button.setFixedHeight(36)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: white;
                    padding: 8px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
            """)
            # Patch: Use self.update_order_status_and_reload to update and reload UI
            button.clicked.connect(lambda: self.update_order_status_and_reload(order_id, next_status))
            return button

        if status == "Onay Bekleyen Sipariş":
            self.cancel_button = create_action_button("İptal Et", "İptal", "#ff3b30", "#ff5e57")
            self.ready_button = create_action_button("Onayla", "Onaylandı", "#34c759", "#5cd17b")
            self.actions_layout.insertWidget(0, self.cancel_button, alignment=Qt.AlignLeft)
            self.actions_layout.addWidget(self.ready_button, alignment=Qt.AlignRight)
        elif status == "Onaylandı":
            self.ready_button = create_action_button("Hazırlanıyor", "Hazırlanıyor", "#34c759", "#5cd17b")
            self.actions_layout.addWidget(self.ready_button, alignment=Qt.AlignRight)
        elif status == "Hazırlanıyor":
            self.ready_button = create_action_button("Hazır", "Hazır", "#34c759", "#5cd17b")
            self.actions_layout.addWidget(self.ready_button, alignment=Qt.AlignRight)
        elif status == "Hazır":
            self.ready_button = create_action_button("Yola Çıkar", "Yolda", "#34c759", "#5cd17b")
            self.actions_layout.addWidget(self.ready_button, alignment=Qt.AlignRight)
        elif status == "Yolda":
            self.ready_button = create_action_button("Teslim Edildi", "Teslim Edildi", "#34c759", "#5cd17b")
            self.actions_layout.addWidget(self.ready_button, alignment=Qt.AlignRight)


    def update_order_status_and_reload(self, order_id, new_status):
        update_order_status(order_id, new_status)
        QTimer.singleShot(500, self.load_orders)

    def clear_order_info(self):
        for label in self.info_labels.values():
            label.setText("")
        rows = self.order_summary_grid.rowCount()
        for row in range(1, rows):
            for col in range(3):
                item = self.order_summary_grid.itemAtPosition(row, col)
                if item and item.widget():
                    widget = item.widget()
                    self.order_summary_grid.removeWidget(widget)
                    widget.deleteLater()
        self.total_amount.setText("")
        for i in reversed(range(self.actions_layout.count())):
            widget = self.actions_layout.itemAt(i).widget()
            if widget and widget in (self.cancel_button, self.ready_button):
                self.actions_layout.removeWidget(widget)
                widget.deleteLater()
        self.clear_progress_bar()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = BafettoPage()
    window.show()
    sys.exit(app.exec_())
