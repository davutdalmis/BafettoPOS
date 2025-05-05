from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import Qt

class PaymentWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ödeme Seçenekleri")
        
        self.selected_payment_option = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Başlık
        title_label = QLabel("Ödeme Seçenekleri")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #000000;
        """)
        main_layout.addWidget(title_label)

        # Ödeme seçenekleri grid layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)  # Butonlar arası boşluk

        # Stil tanımları (iOS benzeri renkler ve tasarım)
        button_style_default = """
            QPushButton {
                background-color: #E8ECEF;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: normal;
                color: #000000;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #D2D2D7;
            }
        """

        button_style_orange = """
            QPushButton {
                background-color: #FF9500;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: normal;
                color: #FFFFFF;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E68A00;
            }
        """

        button_style_blue = """
            QPushButton {
                background-color: #007AFF;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: normal;
                color: #FFFFFF;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #005ECB;
            }
        """

        button_style_red = """
            QPushButton {
                background-color: #FF3B30;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: normal;
                color: #FFFFFF;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """

        # Ödeme seçenekleri
        payment_options = [
            ("Parçalı Öde", button_style_default, 0, 0),
            ("Yemek Kartı", button_style_default, 0, 1),
            ("Edenred", button_style_default, 0, 2),
            ("SetCard", button_style_default, 1, 0),
            ("YS Çüzdan", button_style_default, 1, 1),
            ("Sodexo Plus", button_style_default, 1, 2),
            ("Sodexo Online", button_style_default, 2, 0),
            ("Edenred Online", button_style_default, 2, 1),
            ("Ürünleri Marşla", button_style_blue, 3, 0),
            ("Çari Ödeme", button_style_default, 3, 1),
            ("Tutar Girerek Öde", button_style_orange, 0, 3),
            ("Sodexo", button_style_default, 0, 4),
            ("Multinet", button_style_default, 0, 5),
            ("Metropol", button_style_default, 1, 3),
            ("YS Online", button_style_default, 1, 4),
            ("Getir", button_style_default, 1, 5),
            ("Trendyol", button_style_default, 2, 2),
            ("Sodexo Mobil", button_style_default, 2, 3),
            ("Tokenflex", button_style_default, 2, 4),
            ("Multinet Online", button_style_default, 2, 5),
            ("Masayı İkram Yap", button_style_orange, 3, 2),
            ("Servis Ücreti Ekle", button_style_orange, 3, 3),
            ("Tarih Seç", button_style_blue, 3, 4),
            ("Avans Ödeme", button_style_default, 3, 5),
            ("Adisyona Not Ekle", button_style_orange, 0, 6),
            ("Ödenmez", button_style_default, 1, 6),
            ("Vazgeç", button_style_red, 3, 6),
        ]

        # Buton boyutları ve grid boyutlarını hesapla
        button_width = 130  # Buton genişliğini artırdık (120 -> 130)
        button_height = 60  # Buton yüksekliğini artırdık (50 -> 60)
        for text, style, row, col in payment_options:
            button = QPushButton(text)
            button.setStyleSheet(style)
            button.setFixedSize(button_width, button_height)
            button.clicked.connect(lambda checked, t=text: self.select_payment_option(t))
            grid_layout.addWidget(button, row, col)

        main_layout.addWidget(grid_widget)
        main_layout.addStretch()

        # İptal butonu
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
                color: #007AFF;
            }
            QPushButton:hover {
                background-color: #E8ECEF;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Pencere boyutunu dinamik olarak ayarla
        self.adjust_window_size(grid_layout, button_width, button_height)

    def adjust_window_size(self, grid_layout, button_width, button_height):
        # Grid'deki satır ve sütun sayısını belirle
        row_count = grid_layout.rowCount()
        col_count = grid_layout.columnCount()

        # Grid'in toplam boyutunu hesapla (buton boyutları + boşluklar + kenar boşlukları)
        grid_width = col_count * button_width + (col_count - 1) * grid_layout.spacing() + 40  # 40: kenar boşlukları
        grid_height = row_count * button_height + (row_count - 1) * grid_layout.spacing()

        # Başlık, iptal butonu ve diğer boşluklar için ek yükseklik
        extra_height = 120  # Başlık, iptal butonu ve boşluklar için yaklaşık yükseklik

        # Toplam pencere boyutunu ayarla
        total_width = grid_width + 40  # Ekstra kenar boşlukları
        total_height = grid_height + extra_height + 40  # Ekstra kenar boşlukları

        # Minimum boyutları belirle (içerik taşmasını önlemek için)
        self.setMinimumSize(max(total_width, 400), max(total_height, 300))
        self.resize(total_width, total_height)

    def select_payment_option(self, option):
        self.selected_payment_option = option
        self.accept()

    def get_selected_payment_option(self):
        return self.selected_payment_option