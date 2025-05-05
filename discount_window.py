from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMenu, QButtonGroup, QLineEdit, QGridLayout, QWidget
from PyQt5.QtCore import Qt

class DiscountWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("İskonto Ekle")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: #F5F5F7;")

        self.discount_percentage = 0.0
        self.discount_reason = "Seçilmedi"

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Başlık
        title_label = QLabel("İskonto Ekle")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #1D1D1F;
        """)
        main_layout.addWidget(title_label)

        # İndirim yüzdesi butonları (%10, %20, %50, Özel)
        percentage_layout = QHBoxLayout()
        percentage_layout.setSpacing(12)

        # Buton grubu oluştur (yalnızca bir buton seçilebilir)
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)  # Tek seçim sağlar

        percentages = [("10%", 10.0), ("20%", 20.0), ("50%", 50.0)]
        self.percentage_buttons = []  # Butonları saklamak için liste
        for label, value in percentages:
            button = QPushButton(label)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #D2D2D7;
                    border-radius: 10px;
                    padding: 12px;
                    font-size: 16px;
                    font-weight: 500;
                    color: #1D1D1F;
                }
                QPushButton:hover {
                    background-color: #E8ECEF;
                }
                QPushButton:checked {
                    background-color: #007AFF;
                    color: #FFFFFF;
                    border: none;
                }
            """)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, v=value: self.set_discount_percentage(v))
            self.percentage_buttons.append(button)
            self.button_group.addButton(button)
            percentage_layout.addWidget(button)

        # Özel indirim butonu
        custom_button = QPushButton("Özel")
        custom_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D2D2D7;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: 500;
                color: #1D1D1F;
            }
            QPushButton:hover {
                background-color: #E8ECEF;
            }
            QPushButton:checked {
                background-color: #007AFF;
                color: #FFFFFF;
                border: none;
            }
        """)
        custom_button.setCheckable(True)
        custom_button.clicked.connect(self.open_custom_discount_dialog)
        self.percentage_buttons.append(custom_button)
        self.button_group.addButton(custom_button)
        percentage_layout.addWidget(custom_button)

        main_layout.addLayout(percentage_layout)

        # İndirim nedeni butonu
        reason_layout = QHBoxLayout()
        reason_layout.setSpacing(12)
        self.reason_button = QPushButton("Sebep: Seçilmedi")
        self.reason_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D2D2D7;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: 500;
                color: #1D1D1F;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #E8ECEF;
            }
        """)
        self.reason_button.clicked.connect(self.show_reason_menu)
        reason_layout.addWidget(self.reason_button)
        main_layout.addLayout(reason_layout)

        # Seçilen bilgileri gösteren etiket
        self.info_label = QLabel("İndirim: %0 | Sebep: Seçilmedi")
        self.info_label.setStyleSheet("""
            font-size: 14px;
            color: #6E6E73;
            background-color: transparent;
            padding: 6px;
        """)
        main_layout.addWidget(self.info_label)

        main_layout.addStretch()

        # Butonlar (Tamam en sağda, İptal hemen solunda)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        cancel_button = QPushButton("İptal")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D2D2D7;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
                color: #1D1D1F;
            }
            QPushButton:hover {
                background-color: #E8ECEF;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        confirm_button = QPushButton("Tamam")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #005ECB;
            }
        """)
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(confirm_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def set_discount_percentage(self, percentage):
        self.discount_percentage = percentage
        self.update_info_label()

    def open_custom_discount_dialog(self):
        # Özel indirim için tuş takımı diyaloğu
        dialog = QDialog(self)
        dialog.setWindowTitle("Özel İndirim Oranı")
        dialog.setFixedSize(300, 300)  # Pencere boyutunu eski haline getirdik
        dialog.setStyleSheet("background-color: #F5F5F7;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Giriş alanı
        self.custom_input = QLineEdit()
        self.custom_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #D2D2D7;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                color: #1D1D1F;
            }
        """)
        self.custom_input.setPlaceholderText("İndirim oranını girin (%)")
        self.custom_input.setReadOnly(True)  # Tuş takımı ile giriş yapılacak
        self.custom_input.setFixedHeight(40)  # Giriş alanını küçülttük
        layout.addWidget(self.custom_input)

        # Tuş takımı
        keypad_widget = QWidget()
        keypad_layout = QGridLayout(keypad_widget)
        keypad_layout.setSpacing(15)  # Tuşlar arası boşluğu artırdık

        keypad_style = """
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D2D2D7;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;  # Font boyutunu küçülttük
                font-weight: 500;
                color: #1D1D1F;
            }
            QPushButton:hover {
                background-color: #E8ECEF;
            }
        """

        keypad_buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            (".", 3, 0), ("0", 3, 1), ("C", 3, 2),
        ]

        for text, row, col in keypad_buttons:
            button = QPushButton(text)
            button.setStyleSheet(keypad_style)
            button.setFixedSize(80, 40)  # Tuş boyutlarını küçülttük
            if text == "C":
                button.clicked.connect(self.clear_custom_input)
            elif text == ".":
                button.clicked.connect(lambda: self.append_to_custom_input("."))
            else:
                button.clicked.connect(lambda checked, t=text: self.append_to_custom_input(t))
            keypad_layout.addWidget(button, row, col)

        layout.addWidget(keypad_widget)

        # Tamam ve İptal butonları
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("İptal")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D2D2D7;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
                color: #1D1D1F;
            }
            QPushButton:hover {
                background-color: #E8ECEF;
            }
        """)
        cancel_button.setFixedSize(100, 40)  # Buton boyutlarını küçülttük
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        confirm_button = QPushButton("Tamam")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #005ECB;
            }
        """)
        confirm_button.setFixedSize(100, 40)  # Buton boyutlarını küçülttük
        confirm_button.clicked.connect(lambda: self.set_custom_discount(dialog))
        button_layout.addWidget(confirm_button)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        if dialog.exec_():
            pass  # set_custom_discount zaten discount_percentage'ı güncelliyor

    def append_to_custom_input(self, text):
        current_text = self.custom_input.text()
        if text == "." and "." in current_text:
            return  # Birden fazla ondalık nokta engelleniyor
        self.custom_input.setText(current_text + text)

    def clear_custom_input(self):
        self.custom_input.setText("")

    def set_custom_discount(self, dialog):
        try:
            percentage = float(self.custom_input.text())
            if 0 <= percentage <= 100:  # Geçerli bir indirim oranı kontrolü
                self.discount_percentage = percentage
                self.update_info_label()
                dialog.accept()
            else:
                self.custom_input.setText("")  # Geçersizse sıfırla
        except ValueError:
            self.custom_input.setText("")  # Hatalı girişse sıfırla

    def show_reason_menu(self):
        menu = QMenu(self)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setWindowFlags(Qt.Popup | Qt.NoDropShadowWindowHint | Qt.FramelessWindowHint)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #D2D2D7;
                border-radius: 10px;
                padding: 8px;
                font-size: 16px;
                color: #1D1D1F;
                min-width: 300px;
                margin: 0px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 12px 8px;
                margin: 3px 0;
                border-bottom: 1px solid #E8ECEF;
                color: #1D1D1F;
                min-width: 284px;
            }
            QMenu::item:last {
                border-bottom: none;
            }
            QMenu::item:selected {
                background-color: #007AFF;
                color: #FFFFFF;
            }
            QMenu::item:hover {
                background-color: #E8ECEF;
                color: #1D1D1F;
            }
        """)

        reasons = ["Müşteri", "Dost", "Personel"]
        for reason in reasons:
            menu.addAction(reason, lambda r=reason: self.set_discount_reason(r))

        menu.exec_(self.reason_button.mapToGlobal(self.reason_button.rect().bottomLeft()))

    def set_discount_reason(self, reason):
        self.discount_reason = reason
        self.reason_button.setText(f"Sebep: {reason}")
        self.update_info_label()

    def update_info_label(self):
        self.info_label.setText(f"İndirim: %{self.discount_percentage} | Sebep: {self.discount_reason}")

    def get_discount_amount(self, total_price):
        """Toplam fiyata göre indirim miktarını hesaplar."""
        return (self.discount_percentage / 100) * total_price

    def get_discount_info(self):
        """İndirim yüzdesi ve sebebini döndürür."""
        return {
            "percentage": self.discount_percentage,
            "reason": self.discount_reason
        }