import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QLineEdit, QScrollArea, QListWidget, QMenu, QInputDialog, QApplication
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from discount_window import DiscountWindow
from payment_window import PaymentWindow
from delete_reason_window import DeleteReasonWindow

class SiparisPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.total_price = 0.0
        self.selected_pizzas = []
        self.original_orders = []
        self.quantity = 1

        self.setStyleSheet("background-color: #f2f2f7;")
        self.setAutoFillBackground(True)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        navbar_widget = QWidget()
        navbar_widget.setStyleSheet("background-color: #f2f2f7; border-bottom: 1px solid #d3d3d3;")
        navbar_layout = QHBoxLayout(navbar_widget)
        navbar_layout.setContentsMargins(10, 5, 10, 5)
        navbar_layout.setSpacing(40)

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
        gri_pixmap = QPixmap(20, 20)
        gri_pixmap.fill(Qt.transparent)
        painter = QPainter(gri_pixmap)
        painter.drawPixmap(0, 0, default_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(gri_pixmap.rect(), QColor("#666"))
        painter.end()
        back_icon.setPixmap(gri_pixmap)
        back_icon.setFixedSize(20, 20)

        back_button = QPushButton("Geri")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #666;
            }
            QPushButton:hover {
                color: #666;
            }
        """)
        back_button.clicked.connect(self.go_back_to_main)

        back_layout.addWidget(back_icon)
        back_layout.addWidget(back_button)

        back_wrapper.setProperty("class", "back-wrapper")
        back_wrapper.setStyleSheet("""
            .back-wrapper:hover QPushButton {
                color: #666;
            }
        """)

        navbar_layout.addWidget(back_wrapper)

        title_label = QLabel("Sipariş Ekranı")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        navbar_layout.addWidget(title_label)
        navbar_layout.addStretch()

        navbar_widget.setFixedHeight(60)

        # Sol Sidebar
        left_sidebar_widget = QWidget()
        left_sidebar_widget.setStyleSheet("background-color: #ffffff; border-right: 1px solid #d3d3d3;")
        left_sidebar_layout = QVBoxLayout(left_sidebar_widget)
        left_sidebar_layout.setContentsMargins(10, 10, 10, 10)
        left_sidebar_layout.setSpacing(10)
        left_sidebar_widget.setFixedWidth(300)

        top_button_container = QHBoxLayout()
        top_button_container.setSpacing(12)

        adisyon_button = QPushButton("Adisyon Çıkart")
        adisyon_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        adisyon_button.setFixedSize(132, 40)

        self.exit_button = QPushButton("Çık")
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        self.exit_button.setFixedSize(132, 40)
        self.exit_button.clicked.connect(self.handle_exit_button)

        top_button_container.addWidget(adisyon_button)
        top_button_container.addWidget(self.exit_button)
        left_sidebar_layout.addLayout(top_button_container)

        self.selected_items_list = QListWidget()
        self.selected_items_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: none;
                padding: 5px;
                font-size: 14px;
                color: #333;
            }
            QListWidget::item {
                height: 40px;
                padding: 5px;
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: #333;
                outline: none;
            }
        """)
        self.selected_items_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selected_items_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selected_items_list.itemClicked.connect(self.show_context_menu)
        left_sidebar_layout.addWidget(self.selected_items_list, stretch=1)

        bottom_button_container = QVBoxLayout()
        bottom_button_container.setSpacing(10)

        self.total_button = QPushButton("₺0.00")
        self.total_button.setStyleSheet("""
            QPushButton {
                background-color: #f2f2f7;
                border: 1px solid #d3d3d3;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.total_button.setFixedSize(280, 40)
        bottom_button_container.addWidget(self.total_button)

        bottom_buttons = [
            ("Nakit Kapat", "SİL"),
            ("Kredi Kartı", "İskonto"),
            ("Diğer", "Birleştir")
        ]

        for (left_text, right_text) in bottom_buttons:
            button_row = QHBoxLayout()
            button_row.setSpacing(10)

            left_button = QPushButton(left_text)
            left_button.setStyleSheet("""
                QPushButton {
                    background-color: #f2f2f7;
                    border: 1px solid #d3d3d3;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            left_button.setFixedSize(135, 40)
            if left_text == "Diğer":
                left_button.clicked.connect(self.open_payment_window)
            button_row.addWidget(left_button)

            right_button = QPushButton(right_text)
            right_button.setStyleSheet("""
                QPushButton {
                    background-color: #f2f2f7;
                    border: 1px solid #d3d3d3;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            right_button.setFixedSize(135, 40)
            if right_text == "SİL":
                right_button.clicked.connect(self.delete_selected_item)
            elif right_text == "İskonto":
                right_button.clicked.connect(self.open_discount_window)
            button_row.addWidget(right_button)

            bottom_button_container.addLayout(button_row)

        left_sidebar_layout.addLayout(bottom_button_container)

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f2f2f7;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #f2f2f7; border: none;")

        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: #f2f2f7;")
        self.scroll_content_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_content_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_content_layout.setSpacing(20)

        number_layout = QHBoxLayout()
        self.number_label = QLabel("Masa Seçilmedi")
        self.number_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #000000;
            background-color: #d3d3d3;
            border-radius: 5px;
            padding: 5px;
        """)
        number_layout.addWidget(self.number_label)
        number_layout.addStretch()
        self.scroll_content_layout.addLayout(number_layout)

        self.category_title = QLabel("Pizzalar")
        self.category_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)
        self.scroll_content_layout.addWidget(self.category_title)

        self.pizza_layout = QVBoxLayout()
        self.pizza_layout.setSpacing(10)
        self.scroll_content_layout.addLayout(self.pizza_layout)
        self.scroll_content_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_widget)
        content_layout.addWidget(self.scroll_area)

        self.load_category_items("pizzas.json", "Pizzalar")

        right_sidebar_widget = QWidget()
        right_sidebar_widget.setStyleSheet("background-color: #ffffff; border-left: 1px solid #d3d3d3;")
        right_sidebar_layout = QVBoxLayout(right_sidebar_widget)
        right_sidebar_layout.setContentsMargins(10, 10, 10, 10)
        right_sidebar_layout.setSpacing(5)
        right_sidebar_widget.setFixedWidth(250)

        button_container = QWidget()
        button_container.setFixedHeight(450)
        button_container.setFixedWidth(224)

        button_style_green = """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 5px;
                padding: 5px;
                margin: 0px;
                font-size: 12px;
                font-weight: normal;
                color: #ffffff;
                text-align: center top;
                padding-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

        button_style_orange = """
            QPushButton {
                background-color: #FF9800;
                border: none;
                border-radius: 5px;
                padding: 5px;
                margin: 0px;
                font-size: 12px;
                font-weight: normal;
                color: #ffffff;
                text-align: center top;
                padding-top: 10px;
            }
            QPushButton:hover {
                background-color: #e68a00;
            }
        """

        button_style_blue = """
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 5px;
                padding: 5px;
                margin: 0px;
                font-size: 12px;
                font-weight: normal;
                color: #ffffff;
                text-align: center top;
                padding-top: 10px;
            }
            QPushButton:hover {
                background-color: #1e87db;
            }
        """

        categories = [
            ("SALON MENÜLERİ", "icons/chef_hat.png", button_style_green, "salon_menuleri.json"),
            ("YAN ÜRÜNLER", "icons/chef_hat.png", button_style_green, "yan_urunler.json"),
            ("TATLI", "icons/chef_hat.png", button_style_green, "tatlilar.json"),
            ("SALATALAR", "icons/chef_hat.png", button_style_green, "salatalar.json"),
            ("TATLILAR", "icons/chef_hat.png", button_style_green, "tatlilar.json"),
            ("İÇECEKLER", "icons/chef_hat.png", button_style_green, "icecekler.json"),
            ("İLAVE ÜRÜNLER", "icons/pot.png", button_style_orange, "ilave_urunler.json"),
            ("PİZZALAR", "icons/pizza_slice.png", button_style_blue, "pizzas.json"),
        ]

        button_width = 110
        button_height = 110
        spacing = 2

        for idx, (text, icon_path, style, json_file) in enumerate(categories):
            button = QPushButton(text, button_container)
            button.setStyleSheet(style)
            button.setFixedSize(button_width, button_height)
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(24, 24))
            button.setContentsMargins(0, 0, 0, 0)
            button.clicked.connect(lambda checked, f=json_file, t=text: self.load_category_items(f, t))
            row = idx // 2
            col = idx % 2
            x = col * (button_width + spacing)
            y = row * (button_height + spacing)
            button.setGeometry(x, y, button_width, button_height)

        centering_layout = QHBoxLayout()
        centering_layout.addStretch()
        centering_layout.addWidget(button_container)
        centering_layout.addStretch()

        right_sidebar_layout.addLayout(centering_layout)
        right_sidebar_layout.addStretch()

        self.text_field = QLineEdit()
        self.text_field.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                color: #333;
            }
        """)
        self.text_field.setFixedHeight(40)
        self.text_field.setReadOnly(True)

        keypad_widget = QWidget()
        keypad_layout = QGridLayout(keypad_widget)
        keypad_layout.setSpacing(5)

        keypad_style = """
            QPushButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """

        keypad_buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            (",", 3, 0), ("0", 3, 1), ("C", 3, 2),
        ]

        for text, row, col in keypad_buttons:
            button = QPushButton(text)
            button.setStyleSheet(keypad_style)
            button.setFixedSize(50, 50)
            if text == "C":
                button.clicked.connect(self.clear_text_field)
            elif text == ",":
                button.clicked.connect(lambda checked, t=text: self.append_to_text_field("."))
            else:
                button.clicked.connect(lambda checked, t=text: self.append_to_text_field(t))
            keypad_layout.addWidget(button, row, col)

        right_sidebar_layout.addWidget(self.text_field)
        right_sidebar_layout.addWidget(keypad_widget)

        vertical_layout = QVBoxLayout()
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_layout.setSpacing(0)
        vertical_layout.addWidget(navbar_widget)
        vertical_layout.addLayout(main_layout)

        main_layout.addWidget(left_sidebar_widget, stretch=0)
        main_layout.addWidget(content_widget, stretch=1)
        main_layout.addWidget(right_sidebar_widget, stretch=0)

        # Overlay widget
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
        self.overlay.resize(self.size())
        self.overlay.hide()
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents)

    def save_order_to_firestore(self, table_name):
        from firebase_admin import firestore
        import datetime

        if not self.selected_pizzas:
            return

        db = firestore.client()

        order_data = {
            "masaId": table_name,
            "siparisDurumu": "Hazırlanıyor",
            "siparisTuru": "Kasa",
            "urunler": [],
            "siparisTarihi": firestore.SERVER_TIMESTAMP
        }

        for item in self.selected_pizzas:
            order_data["urunler"].append({
                "urunAdi": item['item']['name'],
                "boyut": item['item']['size'],
                "fiyat": float(item['item']['price']),
                "miktar": item['quantity'],
                "not": item['note']
            })

        db.collection("masaSiparisleri").add(order_data)
        print(f"Firebase'e sipariş kaydedildi: {order_data}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.resize(self.size())

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def load_category_items(self, json_file, category_name):
        self.clear_layout(self.pizza_layout)
        self.category_title.setText(category_name)

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                items = json.load(file)
        except FileNotFoundError:
            print(f"{json_file} dosyası bulunamadı!")
            items = []

        cards_per_row = 5
        for i in range(0, len(items), cards_per_row):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)

            for j in range(cards_per_row):
                idx = i + j
                if idx < len(items):
                    item = items[idx]
                    card = QPushButton()
                    card.setStyleSheet("""
                        QPushButton {
                            background-color: #ffffff;
                            border: none;
                            border-radius: 5px;
                            padding: 10px;
                            text-align: center;
                        }
                        QPushButton:hover {
                            background-color: #e0e0e0;
                        }
                    """)
                    card.setFixedSize(150, 140)

                    card_layout = QVBoxLayout()
                    card_layout.setContentsMargins(5, 5, 5, 5)

                    name_label = QLabel(f"{item['name']} ({item['size']})")
                    name_label.setStyleSheet("""
                        font-size: 12px;
                        font-weight: bold;
                        color: #333333;
                        background-color: transparent;
                        text-align: center;
                        padding: 2px;
                    """)
                    name_label.setWordWrap(True)
                    card_layout.addWidget(name_label)

                    card_layout.addStretch()

                    price_layout = QHBoxLayout()
                    price_layout.addStretch()
                    price_label = QLabel(f"₺{item['price']}")
                    price_label.setStyleSheet("""
                        font-size: 12px;
                        font-weight: bold;
                        color: #333333;
                        background-color: transparent;
                        text-align: right;
                        padding: 2px;
                    """)
                    price_layout.addWidget(price_label)

                    card_layout.addLayout(price_layout)
                    card.setLayout(card_layout)

                    card.clicked.connect(lambda checked, p=item: self.add_to_selected_items(p))
                    row_layout.addWidget(card)

            row_layout.addStretch()
            self.pizza_layout.addLayout(row_layout)

    def append_to_text_field(self, text):
        current_text = self.text_field.text()
        if text == "." and "." in current_text:
            return
        self.text_field.setText(current_text + text)
        try:
            self.quantity = int(float(self.text_field.text()))
        except ValueError:
            self.quantity = 1

    def clear_text_field(self):
        self.text_field.setText("")
        self.quantity = 1

    def go_back_to_main(self):
        self.parent.show_main_page()

    def add_to_selected_items(self, item):
        item_text = f"{item['name']} ({item['size']})"
        if self.quantity > 1:
            item_text = f"{self.quantity}x {item_text}"
        self.selected_items_list.addItem(item_text)
        self.selected_pizzas.append({'item': item, 'note': '', 'quantity': self.quantity})
        self.total_price += float(item['price']) * self.quantity
        self.update_total_price()
        self.update_exit_button()
        self.clear_text_field()

    def delete_selected_item(self):
        selected_item = self.selected_items_list.currentItem()
        if selected_item:
            table_name = self.number_label.text()
            has_existing_order = table_name in self.parent.table_orders and self.parent.table_orders[table_name].get('orders')
            row = self.selected_items_list.row(selected_item)
            if row >= len(self.selected_pizzas):
                # Eğer indirim ya da özel bir satırsa, indirim ise fiyatı geri ekle
                item_text = self.selected_items_list.item(row).text()
                if item_text.startswith("İndirim:"):
                    # "%25 (Sebep)" formatında gelen metinden yüzdeyi çek
                    try:
                        percentage_str = item_text.split("%")[1].split(" ")[0]
                        percentage = float(percentage_str)
                        discount_amount = self.total_price * (percentage / (100 - percentage))
                        self.total_price += discount_amount
                        self.update_total_price()
                        print(f"İndirim satırı silindi, toplam fiyat geri artırıldı: +₺{discount_amount:.2f}")
                    except Exception as e:
                        print(f"İndirim geri alınırken hata oluştu: {e}")
                self.selected_items_list.takeItem(row)
                self.update_exit_button()
                return
            item = self.selected_pizzas[row]

            # Ürünün original_orders'da olup olmadığını kontrol et
            is_existing_item = False
            if row < len(self.original_orders):
                original_item = self.original_orders[row]
                is_existing_item = (
                    original_item['item']['name'] == item['item']['name'] and
                    original_item['quantity'] == item['quantity'] and
                    original_item['note'] == item['note']
                )

            if has_existing_order and is_existing_item:
                # Önceden sipariş edilmiş bir ürünse, silme sebebi penceresini aç
                self.overlay.show()
                self.overlay.raise_()
                reason_dialog = DeleteReasonWindow(self)
                if reason_dialog.exec_():
                    reason = reason_dialog.get_selected_reason()
                    self.selected_pizzas.pop(row)
                    self.total_price -= float(item['item']['price']) * item['quantity']
                    self.selected_items_list.takeItem(row)
                    self.update_total_price()
                    self.update_exit_button()
                    print(f"Ürün silindi, masa: {table_name}, ürün: {item['item']['name']}, sebep: {reason}, selected_pizzas: {self.selected_pizzas}")
                    self.parent.update_table_button_color(table_name)
                self.overlay.hide()
            else:
                self.selected_pizzas.pop(row)
                self.total_price -= float(item['item']['price']) * item['quantity']
                self.selected_items_list.takeItem(row)
                self.update_total_price()
                self.update_exit_button()
                print(f"Ürün silindi, masa: {table_name}, ürün: {item['item']['name']}, selected_pizzas: {self.selected_pizzas}")
                self.parent.update_table_button_color(table_name)

    def open_discount_window(self):
        self.overlay.show()
        self.overlay.raise_()
        discount_dialog = DiscountWindow(self)
        if discount_dialog.exec_():
            discount_info = discount_dialog.get_discount_info()
            discount_amount = discount_dialog.get_discount_amount(self.total_price)
            if discount_amount > 0:
                self.total_price -= discount_amount
                self.update_total_price()
                self.update_exit_button()
                self.selected_items_list.addItem(
                    f"İndirim: %{discount_info['percentage']} ({discount_info['reason']})"
                )
                print(f"İndirim uygulandı: ₺{discount_amount:.2f}, Sebep: {discount_info['reason']}")
        self.overlay.hide()

    def open_payment_window(self):
        self.overlay.show()
        self.overlay.raise_()
        payment_dialog = PaymentWindow(self)
        if payment_dialog.exec_():
            selected_option = payment_dialog.get_selected_payment_option()
            if selected_option:
                print(f"Ödeme seçeneği seçildi: {selected_option}")
        self.overlay.hide()

    def update_total_price(self):
        self.total_button.setText(f"₺{self.total_price:.2f}")

    def update_table_name(self, table_name):
        from PyQt5.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QLabel
        from PyQt5.QtGui import QColor
        print(f"[LOG] update_table_name() çağrıldı - Masa: {table_name}")
        print(f"[DEBUG] Masa adı: {table_name}")
        self.number_label.setText(table_name)
        self.selected_items_list.clear()
        self.selected_pizzas = []
        self.total_price = 0.0

        if table_name in self.parent.table_orders:
            orders = self.parent.table_orders[table_name].get('orders', [])
            for order in orders:
                # First, handle orders with 'urunler'
                if 'urunler' in order:
                    print(f"[DEBUG] Sipariş ham verisi: {order}")
                    for urun in order.get('urunler', []):
                        print(f"[DEBUG] Ürün verisi: {urun}")
                        item = {
                            'name': urun.get('urunAdi', 'Bilinmeyen Ürün'),
                            'size': urun.get('boyut', 'Orta'),
                            'price': urun.get('fiyat', 0.0)
                        }
                        quantity = urun.get('miktar', 1)
                        note = urun.get('not', '')
                        print(f"[DEBUG] İşlenmiş ürün: {item}, adet: {quantity}, not: {note}")
                        self.selected_pizzas.append({'item': item, 'note': note, 'quantity': quantity})

                        # Yeni görsel öğe ile ekleme
                        list_item = QListWidgetItem()
                        item_widget = QWidget()
                        layout = QVBoxLayout(item_widget)
                        layout.setContentsMargins(12, 8, 12, 8)
                        layout.setSpacing(2)
                        item_widget.setMinimumHeight(50)

                        main_text = f"{quantity}x {item['name']} ({item['size']})" if quantity > 1 else f"{item['name']} ({item['size']})"
                        label_main = QLabel(main_text)
                        label_main.setStyleSheet("font-size: 14px; color: #333; margin-bottom: 8px;")
                        layout.addWidget(label_main)

                        if note:
                            label_note = QLabel(f"*{note}")
                            label_note.setStyleSheet("""
                                font-size: 11px;
                                color: #666;
                                background-color: transparent;
                                padding: 6px 8px;
                                margin-top: 4px;
                                min-height: 20px;
                            """)
                            layout.addWidget(label_note)
                            list_item.setBackground(QColor(255, 230, 230))  # Not varsa arka plan kırmızı

                        list_item.setSizeHint(item_widget.sizeHint())
                        self.selected_items_list.addItem(list_item)
                        self.selected_items_list.setItemWidget(list_item, item_widget)
                        self.total_price += float(item['price']) * quantity
                        print(f"[DEBUG] Güncellenen toplam fiyat: {self.total_price:.2f}")
                # Now, handle orders with 'item' key (masa kaydı)
                elif 'item' in order:
                    print(f"[DEBUG] Sipariş ham verisi (masa kaydı): {order}")
                    item = order.get('item', {})
                    name = item.get('name', 'Bilinmeyen Ürün')
                    size = item.get('size', 'Orta')
                    price = item.get('price', 0.0)
                    quantity = order.get('quantity', 1)
                    note = order.get('note', '')

                    item_data = {
                        'name': name,
                        'size': size,
                        'price': price
                    }
                    self.selected_pizzas.append({'item': item_data, 'note': note, 'quantity': quantity})

                    from PyQt5.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QLabel
                    from PyQt5.QtGui import QColor
                    list_item = QListWidgetItem()
                    item_widget = QWidget()
                    layout = QVBoxLayout(item_widget)
                    layout.setContentsMargins(12, 8, 12, 8)
                    layout.setSpacing(2)
                    item_widget.setMinimumHeight(50)

                    main_text = f"{quantity}x {name} ({size})" if quantity > 1 else f"{name} ({size})"
                    label_main = QLabel(main_text)
                    label_main.setStyleSheet("font-size: 14px; color: #333; margin-bottom: 8px;")
                    layout.addWidget(label_main)

                    if note:
                        label_note = QLabel(f"*{note}")
                        label_note.setStyleSheet("""
                            font-size: 11px;
                            color: #666;
                            background-color: transparent;
                            padding: 6px 8px;
                            margin-top: 4px;
                            min-height: 20px;
                        """)
                        layout.addWidget(label_note)
                        list_item.setBackground(QColor(255, 230, 230))

                    list_item.setSizeHint(item_widget.sizeHint())
                    self.selected_items_list.addItem(list_item)
                    self.selected_items_list.setItemWidget(list_item, item_widget)
                    self.total_price += float(price) * quantity
                    print(f"[DEBUG] Güncellenen toplam fiyat (masa kaydı): {self.total_price:.2f}")

        self.original_orders = self.selected_pizzas.copy()
        print(f"[LOG] update_table_name() tamamlandı - Toplam ürün: {len(self.selected_pizzas)}, Toplam fiyat: ₺{self.total_price:.2f}")
        self.update_total_price()
        self.update_exit_button()

    def update_exit_button(self):
        table_name = self.number_label.text()
        has_existing_order = table_name in self.parent.table_orders and self.parent.table_orders[table_name].get('orders')
        
        # Yeni ürün eklenip eklenmediğini kontrol et
        has_new_item = len(self.selected_pizzas) > len(self.original_orders) or any(
            self.selected_pizzas[i]['item']['name'] not in [order['item']['name'] for order in self.original_orders] or
            self.selected_pizzas[i]['quantity'] != self.original_orders[i]['quantity'] or
            self.selected_pizzas[i]['note'] != self.original_orders[i]['note']
            for i in range(min(len(self.selected_pizzas), len(self.original_orders)))
        )

        if self.selected_items_list.count() == 0:
            # Sipariş listesi boşsa "Çık" butonu
            self.exit_button.setText("Çık")
            self.exit_button.setStyleSheet("""
                QPushButton {
                    background-color: #ff0000;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)
        elif has_new_item or not has_existing_order:
            # Yeni ürün eklenmişse veya hiç sipariş yoksa "Sipariş Ver" butonu
            self.exit_button.setText("Sipariş Ver")
            self.exit_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(76, 175, 80, 0.7);
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: rgba(69, 160, 73, 0.7);
                }
            """)
        else:
            self.exit_button.setText("Çık")
            self.exit_button.setStyleSheet("""
                QPushButton {
                    background-color: #ff0000;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)

    def handle_exit_button(self):
        table_name = self.number_label.text()
        print(f"[LOG] handle_exit_button() çağrıldı - Buton: {self.exit_button.text()}, Masa: {table_name}")

        if self.exit_button.text() == "Çık":
            # Eğer sipariş yoksa, masayı sil
            if self.selected_items_list.count() == 0 and not self.selected_pizzas:
                self.parent.table_orders.pop(table_name, None)
                print(f"[LOG] Masa siliniyor: {table_name}")
            else:
                print(f"[LOG] Masa korunuyor (veri var): {table_name}")
            self.parent.update_table_button_color(table_name)
            self.go_back_to_main()
        else:
            self.save_order_to_firestore(table_name)
            print(f"Sipariş kaydedildi, masa: {table_name}, table_orders: {self.parent.table_orders}")
            self.parent.show_main_page()
            self.parent.update_table_button_color(table_name)

    def show_context_menu(self, item):
        if not item:
            return

        menu = QMenu(self)
        menu.setAttribute(Qt.WA_TranslucentBackground, True)
        menu.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        
        menu.setStyleSheet("""
            QMenu {
                background-color: transparent;
                padding: 8px;
                margin: 0px;
            }
            QMenu::item {
                background-color: rgba(242, 242, 247, 0.95);
                border: 0.5px solid rgba(0, 0, 0, 0.2);
                border-radius: 12px;
                padding: 12px 20px;
                margin: 2px 4px;
                font-size: 17px;
                color: #000000;
            }
            QMenu::item:selected {
                background-color: #007AFF;
                color: #ffffff;
            }
            QMenu::item:hover {
                background-color: rgba(0, 122, 255, 0.1);
                color: #000000;
            }
        """)

        delete_action = menu.addAction("Sil")
        add_note_action = menu.addAction("Not Ekle")

        menu.setMinimumWidth(180)
        menu.setMinimumHeight(100)

        cursor_pos = self.selected_items_list.mapToGlobal(self.selected_items_list.visualItemRect(item).center())
        action = menu.exec_(cursor_pos)

        if action == delete_action:
            self.delete_selected_item()
        elif action == add_note_action:
            self.add_note_to_item()

    def add_note_to_item(self):
        selected_item = self.selected_items_list.currentItem()
        if selected_item:
            row = self.selected_items_list.row(selected_item)
            if row >= len(self.selected_pizzas):
                return

            existing_note = self.selected_pizzas[row].get('note', '')

            self.selected_items_list.item(row).setBackground(QColor(255, 230, 230))

            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)

            note_input = QLineEdit()
            note_input.setPlaceholderText("Not girin...")
            note_input.setText(existing_note)
            note_input.setStyleSheet("""
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 13px;
                    color: #333;
                }
            """)
            container_layout.addWidget(note_input)

            save_button = QPushButton("Tamam")
            save_button.setFixedHeight(30)
            save_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            save_button.clicked.connect(lambda: self.save_inline_note(note_input, row))
            container_layout.addWidget(save_button)

            # Varsa eski not alanı kaldır
            if self.selected_items_list.item(row + 1) and self.selected_items_list.itemWidget(self.selected_items_list.item(row + 1)):
                self.selected_items_list.takeItem(row + 1)

            self.selected_items_list.insertItem(row + 1, "")
            self.selected_items_list.setItemWidget(self.selected_items_list.item(row + 1), container)
            self.selected_items_list.setCurrentRow(row + 1)


    def save_inline_note(self, note_input, row):
        note = note_input.text().strip()
        self.selected_pizzas[row]['note'] = note
        item = self.selected_pizzas[row]

        item_widget = QWidget()
        layout = QVBoxLayout(item_widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(0)
        item_widget.setMinimumHeight(50)

        main_text = f"{item['quantity']}x {item['item']['name']} ({item['item']['size']})" if item['quantity'] > 1 else f"{item['item']['name']} ({item['item']['size']})"
        label_main = QLabel(main_text)
        label_main.setStyleSheet("font-size: 14px; color: #333; margin-bottom: 8px;")
        layout.addWidget(label_main)

        if note:
            label_note = QLabel(f"*{note}")
            label_note.setStyleSheet("""
                font-size: 11px;
                color: #666;
                background-color: transparent;
                padding: 6px 8px;
                margin-top: 4px;
                min-height: 20px;
            """)
            layout.addWidget(label_note)
            self.selected_items_list.item(row).setBackground(QColor(255, 230, 230))
        else:
            self.selected_items_list.item(row).setBackground(QColor("#f2f2f7"))

        self.selected_items_list.item(row).setSizeHint(item_widget.sizeHint())
        self.selected_items_list.setItemWidget(self.selected_items_list.item(row), item_widget)

        if self.selected_items_list.item(row + 1):
            self.selected_items_list.takeItem(row + 1)

        self.update_exit_button()
        self.parent.table_orders[self.number_label.text()] = {
            'orders': self.selected_pizzas.copy(),
            'total_price': self.total_price
        }

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SiparisPage()
    window.show()
    sys.exit(app.exec_())