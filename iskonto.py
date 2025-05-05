from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMenu
from PyQt5.QtCore import Qt

class DiscountWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("İskonto Ekle")
        self.setFixedSize(350, 350)
        self.setStyleSheet("background-color: #f2f2f7;")

        self.discount_percentage = 0.0
        self.discount_reason = "Seçilmedi"

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Başlık
        title_label = QLabel("İskonto Ekle")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
        """)
        main_layout.addWidget(title_label)

        # İndirim yüzdesi butonları (%10, %20, %50)
        percentage_layout = QHBoxLayout()
        percentage_layout.setSpacing(10)
        percentages = [("10%", 10.0), ("20%", 20.0), ("50%", 50.0)]
        for label, value in percentages:
            button = QPushButton(label)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #1e87db;
                }
                QPushButton:checked {
                    background-color: #4CAF50;
                }
            """)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, v=value: self.set_discount_percentage(v))
            percentage_layout.addWidget(button)
        main_layout.addLayout(percentage_layout)

        # İndirim nedeni butonu ve menüsü
        reason_layout = QHBoxLayout()
        reason_layout.setSpacing(10)
        self.reason_button = QPushButton("Sebep: Seçilmedi")
        self.reason_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #d3d3d3;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                color: #333;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.reason_button.clicked.connect(self.show_reason_menu)
        reason_layout.addWidget(self.reason_button)
        main_layout.addLayout(reason_layout)

        # Seçilen bilgileri gösteren etiket
        self.info_label = QLabel("İndirim: %0 | Sebep: Seçilmedi")
        self.info_label.setStyleSheet("""
            font-size: 14px;
            color: #333;
            background-color: transparent;
            padding: 5px;
        """)
        main_layout.addWidget(self.info_label)

        main_layout.addStretch()

        # Tamam ve İptal butonları
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        confirm_button = QPushButton("Tamam")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(confirm_button)

        cancel_button = QPushButton("İptal")
        cancel_button.setStyleSheet("""
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
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def set_discount_percentage(self, percentage):
        self.discount_percentage = percentage
        self.update_info_label()

    def show_reason_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2c2c2c;
                border: 1px solid #444;
                border-radius: 12px;
                padding: 8px;
                font-size: 16px;
                color: #ffffff;
            }
            QMenu::item {
                background-color: transparent;
                padding: 12px 24px;
                margin: 3px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
                color: #ffffff;
            }
            QMenu::item:hover {
                background-color: #666666;
                color: #ffffff;
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