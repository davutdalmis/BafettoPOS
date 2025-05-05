from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt

class DeleteReasonWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Silme Sebebi")
        self.setFixedSize(300, 150)
        self.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
        self.selected_reason = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Açıklama etiketi
        message_label = QLabel("Yemeğin silinme sebebini seçin:")
        message_label.setStyleSheet("font-size: 14px; color: #333;")
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)

        # Seçenekler için QComboBox
        self.reason_combo = QComboBox()
        self.reason_combo.addItems([
            "Müşteri iptal etti",
            "Hatalı sipariş",
            "Müşteri iade etti",
            "Diğer"
        ])
        self.reason_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #d3d3d3;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                color: #333;
            }
            QComboBox:hover {
                background-color: #e0e0e0;
            }
        """)
        layout.addWidget(self.reason_combo)

        # Butonlar
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

        confirm_button = QPushButton("Onayla")
        confirm_button.setStyleSheet(button_style)
        confirm_button.clicked.connect(self.accept)

        cancel_button = QPushButton("İptal")
        cancel_button.setStyleSheet(button_style)
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def get_selected_reason(self):
        return self.reason_combo.currentText()