import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QHBoxLayout, QWidget, QLabel, QPushButton, QListWidgetItem, QVBoxLayout, QFrame, QDialog, QStackedWidget
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl

# Ses çalma fonksiyonu (bildirim için)
def oynat_sesi(sound_path):
    try:
        effect = QSoundEffect()
        effect.setSource(QUrl.fromLocalFile(sound_path))
        effect.setLoopCount(1)
        effect.setVolume(0.9)
        effect.play()
    except Exception as e:
        print(f"[ERROR] QSoundEffect ile ses çalınamadı: {e}")
import firebase_admin
from firebase_admin import credentials, firestore
import yonetim  # yonetim.py dosyasını içe aktar
import yemeksepeti  # yemeksepeti.py dosyasını içe aktar
import getiryemek  # getiryemek.py dosyasını içe aktar
import trendyolGo  # trendyolGo.py dosyasını içe aktar
import bafetto  # bafetto.py dosyasını içe aktar

import siparis  # SiparisPage sınıfını içe aktar

# Firebase başlatma (AnaSayfa.py'de de gerekli)
try:
    cred = credentials.Certificate("bafetto-d00f2-firebase-adminsdk-fbsvc-408b279d45.json")
    if not firebase_admin.get_app():
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    db = None

class ExitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Çıkış Onayı")
        self.setFixedSize(300, 150)
        self.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        message_label = QLabel("Çıkış yapmak istediğinizden emin misiniz?")
        message_label.setStyleSheet("font-size: 14px; color: #333;")
        message_label.setAlignment(Qt.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        button_style = """
            QPushButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                color: #333;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """

        yes_button = QPushButton("Evet")
        yes_button.setStyleSheet(button_style)
        yes_button.clicked.connect(self.accept)

        no_button = QPushButton("Hayır")
        no_button.setStyleSheet(button_style)
        no_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        button_layout.addStretch()

        layout.addWidget(message_label)
        layout.addLayout(button_layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BafettoPOS")
        
        self.showMaximized()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint)

        self.table_orders = {}

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_page = QWidget()
        main_layout = QHBoxLayout(self.main_page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel_widget = QWidget()
        left_panel_layout = QVBoxLayout(left_panel_widget)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.setSpacing(0)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(10)

        logo_label = QLabel()
        logo_label.setPixmap(QIcon("images/bafetto.png").pixmap(40, 40))
        logo_label.setFixedSize(40, 40)

        branch_label = QLabel("BAFETTO POS")
        branch_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")

        header_layout.addWidget(logo_label)
        header_layout.addWidget(branch_label)
        header_layout.addStretch()

        header_widget.setFixedHeight(60)
        header_widget.setStyleSheet("background-color: #f0f0f0;")
        left_panel_layout.addWidget(header_widget)

        self.order_list = QListWidget()
        self.order_list.setFixedWidth(300)
        self.order_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.order_list.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                padding: 0px;
            }
            QListWidget::item {
                margin-bottom: 0px;
                padding: 0px;
            }
            QListWidget::item:selected {
                background-color: #1e90ff;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)

        self.labels = []

        # Initial load of orders
        self.load_orders()
        # Start listening for real-time updates
        self.listen_to_orders()
        self.listen_to_masa_orders()

        self.order_list.itemSelectionChanged.connect(self.update_label_colors)

        left_panel_layout.addWidget(self.order_list)

        # Sağ panel
        right_panel_widget = QWidget()
        right_panel_widget.setStyleSheet("background-color: #1c2526;")
        right_panel_layout = QVBoxLayout(right_panel_widget)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(0)

        navbar_widget = QWidget()
        navbar_widget.setStyleSheet("background-color: white;")
        navbar_layout = QHBoxLayout(navbar_widget)
        navbar_layout.setContentsMargins(10, 5, 10, 5)
        navbar_layout.setSpacing(20)

        # Buton stilleri
        self.button_style_selected = """
            QPushButton {
                background-color: #d4edda;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: #c3e6cb;
            }
        """

        self.button_style_unselected = """
            QPushButton {
                background-color: white;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """

        self.yemeksepeti_button_style_unselected = """
            QPushButton {
                background-color: rgba(204, 0, 0, 0.2);
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(204, 0, 0, 0.3);
            }
        """

        self.yemeksepeti_button_style_selected = """
            QPushButton {
                background-color: rgba(204, 0, 0, 0.4);
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(204, 0, 0, 0.5);
            }
        """

        self.getir_button_style_unselected = """
            QPushButton {
                background-color: rgba(87, 0, 127, 0.2);
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(87, 0, 127, 0.3);
            }
        """

        self.getir_button_style_selected = """
            QPushButton {
                background-color: rgba(87, 0, 127, 0.4);
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(87, 0, 127, 0.5);
            }
        """

        self.trendyol_button_style_unselected = """
            QPushButton {
                background-color: rgba(242, 122, 26, 0.2);
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(242, 122, 26, 0.3);
            }
        """

        self.trendyol_button_style_selected = """
            QPushButton {
                background-color: rgba(242, 122, 26, 0.4);
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(242, 122, 26, 0.5);
            }
        """

        self.bafetto_button_style_unselected = """
            QPushButton {
                background-color: rgba(255, 0, 0, 0.2);
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.3);
            }
        """

        self.bafetto_button_style_selected = """
            QPushButton {
                background-color: rgba(255, 0, 0, 0.4);
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.5);
            }
        """

        self.salon_button = QPushButton("Salon\n0/11")
        self.salon_button.setStyleSheet(self.button_style_selected)
        self.salon_button.setFixedHeight(50)
        self.salon_button.setFixedWidth(120)
        self.salon_button.clicked.connect(self.show_salon_tables)

        self.bahce_button = QPushButton("Bahçe\n0/7")
        self.bahce_button.setStyleSheet(self.button_style_unselected)
        self.bahce_button.setFixedHeight(50)
        self.bahce_button.setFixedWidth(120)
        self.bahce_button.clicked.connect(self.show_bahce_tables)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #d3d3d3; max-width: 1px;")
        separator.setFixedHeight(30)

        self.yemeksepeti_button = QPushButton("YemekSepeti\n0/0")
        self.yemeksepeti_button.setStyleSheet(self.yemeksepeti_button_style_unselected)
        self.yemeksepeti_button.setFixedHeight(50)
        self.yemeksepeti_button.setFixedWidth(120)
        self.yemeksepeti_button.clicked.connect(self.show_yemeksepeti_page)

        self.getir_button = QPushButton("Getir\n0/0")
        self.getir_button.setStyleSheet(self.getir_button_style_unselected)
        self.getir_button.setFixedHeight(50)
        self.getir_button.setFixedWidth(120)
        self.getir_button.clicked.connect(self.show_getiryemek_page)

        self.trendyol_button = QPushButton("TrendyolGo\n0/0")
        self.trendyol_button.setStyleSheet(self.trendyol_button_style_unselected)
        self.trendyol_button.setFixedHeight(50)
        self.trendyol_button.setFixedWidth(120)
        self.trendyol_button.clicked.connect(self.show_trendyolgo_page)

        # Bafetto button (restore)
        self.bafetto_button = QPushButton("Bafetto\n0/0")
        self.bafetto_button.setStyleSheet(self.bafetto_button_style_unselected)
        self.bafetto_button.setFixedHeight(50)
        self.bafetto_button.setFixedWidth(120)
        self.bafetto_button.clicked.connect(self.show_bafetto_page)

        self.navbar_buttons = [
            self.salon_button,
            self.bahce_button,
            self.yemeksepeti_button,
            self.getir_button,
            self.trendyol_button,
            self.bafetto_button,
        ]

        navbar_layout.addWidget(self.salon_button)
        navbar_layout.addWidget(self.bahce_button)
        navbar_layout.addWidget(separator)
        navbar_layout.addWidget(self.yemeksepeti_button)
        navbar_layout.addWidget(self.getir_button)
        navbar_layout.addWidget(self.trendyol_button)
        navbar_layout.addWidget(self.bafetto_button)

        navbar_layout.addStretch()

        settings_button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #333;
            }
            QPushButton:hover {
                color: #1e90ff;
            }
        """

        exit_button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #ff0000;
            }
            QPushButton:hover {
                color: #cc0000;
            }
        """

        self.settings_button = QPushButton("Yönetim")
        self.settings_button.setStyleSheet(settings_button_style)
        self.settings_button.clicked.connect(self.show_settings_page)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #d3d3d3; max-width: 1px;")
        separator2.setFixedHeight(30)

        exit_button = QPushButton("Çıkış Yap")
        exit_button.setStyleSheet(exit_button_style)
        exit_button.clicked.connect(self.show_exit_dialog)

        navbar_layout.addWidget(self.settings_button)
        navbar_layout.addWidget(separator2)
        navbar_layout.addWidget(exit_button)

        navbar_widget.setFixedHeight(60)

        right_panel_layout.addWidget(navbar_widget)

        self.table_buttons_widget = QWidget()
        self.table_buttons_layout = QHBoxLayout(self.table_buttons_widget)
        self.table_buttons_layout.setContentsMargins(10, 10, 10, 0)
        self.table_buttons_layout.setSpacing(10)
        self.table_buttons_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.table_button_style = """
            QPushButton {
                background-color: white;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding-top: 10px;
                padding-bottom: 30px;
                font-size: 12px;
                font-weight: normal;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """

        self.show_salon_tables()

        right_panel_layout.addWidget(self.table_buttons_widget)

        main_layout.addWidget(left_panel_widget, stretch=0)
        main_layout.addWidget(right_panel_widget, stretch=1)

        self.stacked_widget.addWidget(self.main_page)

        self.settings_window = yonetim.YonetimWindow(self)
        self.settings_page = self.settings_window.centralWidget()
        self.stacked_widget.addWidget(self.settings_page)

        self.yemeksepeti_window = yemeksepeti.YemekSepetiPage(self)
        self.yemeksepeti_page = self.yemeksepeti_window
        self.stacked_widget.addWidget(self.yemeksepeti_page)

        self.getiryemek_window = getiryemek.GetirYemekPage(self)
        self.getiryemek_page = self.getiryemek_window
        self.stacked_widget.addWidget(self.getiryemek_page)

        self.trendyolgo_window = trendyolGo.TrendyolGoPage(self)
        self.trendyolgo_page = self.trendyolgo_window
        self.stacked_widget.addWidget(self.trendyolgo_page)

        # Add Bafetto window and page to stacked widget
        self.bafetto_window = bafetto.BafettoPage(self)
        self.bafetto_page = self.bafetto_window
        self.stacked_widget.addWidget(self.bafetto_page)

        self.siparis_window = siparis.SiparisPage(self)
        self.siparis_page = self.siparis_window
        self.stacked_widget.addWidget(self.siparis_page)

    def load_orders(self):
        # Only GetirYemek orders are loaded now
        orders = getiryemek.get_active_orders()

        # Clear existing items in the order list
        self.order_list.clear()
        self.labels.clear()

        for i, order in enumerate(orders):
            item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QVBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(5)

            # Title: Platform and Status
            platform = "GetirYemek Sipariş"
            status = order.get('siparisDurumu', 'Bilinmeyen')
            title = f"{platform} ({status})"
            title_label = QLabel(title)
            title_label.setWordWrap(True)
            title_label.setStyleSheet("font-weight: bold; color: #333; padding: 5px;")
            title_label.setFixedWidth(300)
            title_label.adjustSize()

            # Customer name and order details
            user_id = order.get('kullaniciId', 'Müşteri')
            display_name = getiryemek.get_user_display_name(user_id)
            urunler = order.get('urunler', [])
            order_details = f"{display_name}\n"
            for urun in urunler:
                miktar = urun.get('miktar', 1)
                urun_adi = urun.get('urunAdi', 'Bilinmeyen Ürün')
                order_details += f"{miktar} x {urun_adi}\n"
            order_details = order_details.strip()
            details_label = QLabel(order_details)
            details_label.setWordWrap(True)
            details_label.setStyleSheet("color: #666; padding: 5px;")
            details_label.setFixedWidth(300)
            details_label.adjustSize()

            # Order ID and Timestamp
            order_id = order.get('id', '000')[-3:]
            siparis_tarihi = order.get('siparisTarihi')
            order_time = "Bilinmiyor"
            if siparis_tarihi:
                try:
                    order_time = siparis_tarihi.strftime("%d.%m.%y, %H:%M")
                except (AttributeError, ValueError, TypeError):
                    order_time = "Bilinmiyor"
            id_time_label = QLabel(f"bf{order_id}\n{order_time}")
            id_time_label.setWordWrap(True)
            id_time_label.setStyleSheet("color: #999; font-size: 12px; padding: 5px;")
            id_time_label.setFixedWidth(300)
            id_time_label.adjustSize()

            self.labels.append((title_label, details_label, id_time_label))

            item_layout.addWidget(title_label)
            item_layout.addWidget(details_label)
            item_layout.addWidget(id_time_label)

            if i < len(orders) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                separator.setStyleSheet("background-color: #d3d3d3; max-height: 1px; margin: 5px 0px;")
                item_layout.addWidget(separator)

            item_widget.setLayout(item_layout)

            item_widget.setFixedWidth(300)

            total_height = title_label.sizeHint().height() + details_label.sizeHint().height() + id_time_label.sizeHint().height() + 10
            if i < len(orders) - 1:
                total_height += 1
            item_widget.setFixedHeight(total_height)
            item.setSizeHint(QSize(300, total_height))

            self.order_list.addItem(item)
            self.order_list.setItemWidget(item, item_widget)

    def listen_to_orders(self):
        if db is None:
            return
        def on_snapshot(col_snapshot, changes, read_time):
            QTimer.singleShot(0, self.load_orders)
        try:
            active_statuses = ["Onay Bekleyen Sipariş", "Onaylandı", "Hazırlanıyor", "Hazır", "Yolda"]
            db.collection('siparisler').where(
                filter=firestore.FieldFilter('siparisDurumu', 'in', active_statuses)
            ).on_snapshot(on_snapshot)
        except Exception as e:
            pass

    def listen_to_masa_orders(self):
        # Use QSoundEffect for notification
        import os
        if db is None:
            return

        def on_snapshot(col_snapshot, changes, read_time):
            print("[DEBUG] masaSiparisleri güncellendi")
            print(f"[DEBUG] Toplam gelen döküman: {len(col_snapshot)}")
            self.table_orders.clear()
            # Collect existing order IDs before updating with new snapshot
            existing_order_ids = set()
            for orders in self.table_orders.values():
                for order in orders["orders"]:
                    existing_order_ids.add(order.get("id"))

            new_order_detected = False

            for doc in col_snapshot:
                data = doc.to_dict()
                data["id"] = doc.id
                masa_id = data.get("masaId", "")
                if not masa_id:
                    continue
                if masa_id not in self.table_orders:
                    self.table_orders[masa_id] = {"orders": [], "total_price": 0.0}
                print(f"[DEBUG] Sipariş eklendi - masaId: {masa_id}, siparisId: {data['id']}")
                self.table_orders[masa_id]["orders"].append(data)
                # Detect new order
                if data.get("id") not in existing_order_ids:
                    print(f"[DEBUG] Yeni sipariş algılandı: {data['id']}")
                    new_order_detected = True
                urunler = data.get("urunler", [])
                for urun in urunler:
                    self.table_orders[masa_id]["total_price"] += urun.get("fiyat", 0) * urun.get("miktar", 1)

            # Play sound if new masa order detected (using QSoundEffect)
            if new_order_detected:
                sound_path = os.path.join(os.path.dirname(__file__), "sounds", "notification.wav")
                print(f"[DEBUG] Bildirim sesi çalınıyor - {sound_path}")
                print(f"[DEBUG] Dosya var mı: {os.path.exists(sound_path)}")
                QTimer.singleShot(0, lambda: oynat_sesi(sound_path))

            # Only show the tables for the currently selected area
            if self.salon_button.styleSheet() == self.button_style_selected:
                QTimer.singleShot(0, self.show_salon_tables)
            elif self.bahce_button.styleSheet() == self.button_style_selected:
                QTimer.singleShot(0, self.show_bahce_tables)

        try:
            db.collection("masaSiparisleri").where(
                filter=firestore.FieldFilter("siparisDurumu", "in", ["Hazırlanıyor", "Onaylandı", "Hazır"])
            ).on_snapshot(on_snapshot)
        except Exception as e:
            print(f"Masa siparişlerini dinlerken hata oluştu: {e}")

    def show_settings_page(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def show_main_page(self):
        self.stacked_widget.setCurrentWidget(self.main_page)

    def show_yemeksepeti_page(self):
        self.stacked_widget.setCurrentWidget(self.yemeksepeti_page)
        self.update_navbar_button_styles(self.yemeksepeti_button)

    def show_getiryemek_page(self):
        self.stacked_widget.setCurrentWidget(self.getiryemek_page)
        self.update_navbar_button_styles(self.getir_button)

    def show_trendyolgo_page(self):
        self.stacked_widget.setCurrentWidget(self.trendyolgo_page)
        self.update_navbar_button_styles(self.trendyol_button)

    def show_bafetto_page(self):
        self.stacked_widget.setCurrentWidget(self.bafetto_page)
        self.update_navbar_button_styles(self.bafetto_button)

    def show_siparis_page(self, table_name):
        self.siparis_window.update_table_name(table_name)
        self.stacked_widget.setCurrentWidget(self.siparis_page)
        if table_name.startswith("B ") or table_name == "SALONA PAKET":
            self.update_navbar_button_styles(self.bahce_button)
        else:
            self.update_navbar_button_styles(self.salon_button)

    def update_navbar_button_styles(self, selected_button):
        for button in self.navbar_buttons:
            if button == selected_button:
                if button in [self.salon_button, self.bahce_button]:
                    button.setStyleSheet(self.button_style_selected)
                elif button == self.yemeksepeti_button:
                    button.setStyleSheet(self.yemeksepeti_button_style_selected)
                elif button == self.getir_button:
                    button.setStyleSheet(self.getir_button_style_selected)
                elif button == self.trendyol_button:
                    button.setStyleSheet(self.trendyol_button_style_selected)
                elif button == self.bafetto_button:
                    button.setStyleSheet(self.bafetto_button_style_selected)
            else:
                if button == self.yemeksepeti_button:
                    button.setStyleSheet(self.yemeksepeti_button_style_unselected)
                elif button == self.getir_button:
                    button.setStyleSheet(self.getir_button_style_unselected)
                elif button == self.trendyol_button:
                    button.setStyleSheet(self.trendyol_button_style_unselected)
                elif button == self.bafetto_button:
                    button.setStyleSheet(self.bafetto_button_style_unselected)
                else:
                    button.setStyleSheet(self.button_style_unselected)

    def show_salon_tables(self):
        for i in reversed(range(self.table_buttons_layout.count())):
            widget = self.table_buttons_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        salon_tables = ["SALONA PAKET", "1", "2", "3", "4", "5"]
        for table_name in salon_tables:
            button_text = table_name
            if table_name in self.table_orders and self.table_orders[table_name]['orders']:
                button_text += f"\n₺{self.table_orders[table_name]['total_price']:.2f}"
            button = QPushButton(button_text)
            if table_name in self.table_orders and self.table_orders[table_name]['orders']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #FF9797;
                        border: 1px solid #d3d3d3;
                        border-radius: 10px;
                        padding-top: 10px;
                        padding-bottom: 10px;
                        font-size: 12px;
                        font-weight: normal;
                        color: #ffffff;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #FF6C6C;
                    }
                """)
            else:
                button.setStyleSheet(self.table_button_style)
            button.setFixedSize(100, 100)
            button.clicked.connect(lambda checked, name=table_name: self.show_siparis_page(name))
            self.table_buttons_layout.addWidget(button)

        self.update_navbar_button_styles(self.salon_button)

    def show_bahce_tables(self):
        for i in reversed(range(self.table_buttons_layout.count())):
            widget = self.table_buttons_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        bahce_tables = ["B 1", "B 2", "B 3", "B 4"]
        for table_name in bahce_tables:
            button_text = table_name
            if table_name in self.table_orders and self.table_orders[table_name]['orders']:
                button_text += f"\n₺{self.table_orders[table_name]['total_price']:.2f}"
            button = QPushButton(button_text)
            if table_name in self.table_orders and self.table_orders[table_name]['orders']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #FF9797;
                        border: 1px solid #d3d3d3;
                        border-radius: 10px;
                        padding-top: 10px;
                        padding-bottom: 10px;
                        font-size: 12px;
                        font-weight: normal;
                        color: #ffffff;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #FF6C6C;
                    }
                """)
            else:
                button.setStyleSheet(self.table_button_style)
            button.setFixedSize(100, 100)
            button.clicked.connect(lambda checked, name=table_name: self.show_siparis_page(name))
            self.table_buttons_layout.addWidget(button)

        self.update_navbar_button_styles(self.bahce_button)

    def show_exit_dialog(self):
        dialog = ExitDialog(self)
        if dialog.exec_():
            self.close()

    def update_label_colors(self):
        for title_label, details_label, id_time_label in self.labels:
            title_label.setStyleSheet("font-weight: bold; color: #333; padding: 5px;")
            details_label.setStyleSheet("color: #666; padding: 5px;")
            id_time_label.setStyleSheet("color: #999; font-size: 12px; padding: 5px;")

        selected_items = self.order_list.selectedItems()
        for item in selected_items:
            index = self.order_list.row(item)
            if index < len(self.labels):
                title_label, details_label, id_time_label = self.labels[index]
                title_label.setStyleSheet("font-weight: bold; color: white; padding: 5px;")
                details_label.setStyleSheet("color: white; padding: 5px;")
                id_time_label.setStyleSheet("color: white; font-size: 12px; padding: 5px;")

    def update_table_button_color(self, table_name):
        print(f"[LOG] update_table_button_color() çağrıldı - Masa: {table_name}")
        if self.siparis_window.selected_pizzas:
            print(f"[LOG] Masa güncelleniyor - Yeni siparişler kaydediliyor: {table_name}")
            # Eğer masa üzerinde aktif sipariş varsa güncelle
            self.table_orders[table_name] = {
                'orders': self.siparis_window.selected_pizzas.copy(),
                'total_price': self.siparis_window.total_price
            }
        elif table_name in self.table_orders:
            print(f"[LOG] Masa sabit kaldı - Var ama yeni sipariş yok: {table_name}")
            # Masa zaten kayıtlıysa ama yeni sipariş yoksa, dokunma
            pass
        else:
            print(f"[LOG] Masa siliniyor - Yeni boş masa: {table_name}")
            # Yeni ve boş masa kaydını sil
            self.table_orders.pop(table_name, None)

        for i in range(self.table_buttons_layout.count()):
            button = self.table_buttons_layout.itemAt(i).widget()
            if button and button.text().split('\n')[0] == table_name:
                button_text = table_name
                if table_name in self.table_orders and self.table_orders[table_name]['orders']:
                    button_text += f"\n₺{self.table_orders[table_name]['total_price']:.2f}"
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #FF9797;
                            border: 1px solid #d3d3d3;
                            border-radius: 10px;
                            padding-top: 10px;
                            padding-bottom: 10px;
                            font-size: 12px;
                            font-weight: normal;
                            color: #ffffff;
                            text-align: center;
                        }
                        QPushButton:hover {
                            background-color: #FF6C6C;
                        }
                    """)
                else:
                    button.setStyleSheet(self.table_button_style)
                button.setText(button_text)
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())