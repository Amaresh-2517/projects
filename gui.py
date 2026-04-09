import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QLineEdit, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

from encrypt import encrypt_file
from decrypt import decrypt_file


class FileEncryptorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 File Encryption Tool")
        self.setMinimumWidth(520)

        self.file_path = ""

        # Header
        title = QLabel("File Locker")
        title.setObjectName("title")
        subtitle = QLabel("Encrypt and decrypt files locally with a single password.")
        subtitle.setObjectName("subtitle")

        # File chooser row
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        self.file_label.setObjectName("fileLabel")

        choose_row = QHBoxLayout()
        choose_row.addWidget(self.file_label, stretch=1)
        self.select_btn = QPushButton("Choose File")
        self.select_btn.setObjectName("selectBtn")
        self.select_btn.clicked.connect(self.select_file)
        choose_row.addWidget(self.select_btn)

        # Password
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter password (keep it safe!)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Actions
        actions = QHBoxLayout()
        self.encrypt_btn = QPushButton("Encrypt")
        self.encrypt_btn.clicked.connect(self.encrypt)
        self.decrypt_btn = QPushButton("Decrypt")
        self.decrypt_btn.clicked.connect(self.decrypt)
        actions.addWidget(self.encrypt_btn)
        actions.addWidget(self.decrypt_btn)

        # Status bar
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(12, 10, 12, 10)
        self.status_icon = QLabel("⏳")
        self.status = QLabel("Waiting for a file...")
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignLeft)

        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider)
        layout.addLayout(choose_row)
        layout.addWidget(self.password_input)
        layout.addLayout(actions)
        layout.addWidget(status_frame)

        self.setLayout(layout)
        self.apply_styles()

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file:
            self.file_path = file
            self.file_label.setText(f"Selected: {file}")
            self.set_status("Ready to encrypt or decrypt.", "📄")
        else:
            self.set_status("Waiting for a file...", "⏳")

    def encrypt(self):
        if not self.file_path:
            self.set_status("No file selected.", "❌")
            return

        password = self.password_input.text()
        if not password:
            self.set_status("Enter a password first.", "❌")
            return

        try:
            encrypt_file(self.file_path, password)
            self.set_status("File encrypted successfully.", "✅")
        except Exception as e:
            self.set_status(f"Error: {str(e)}", "❌")

    def decrypt(self):
        if not self.file_path:
            self.set_status("No file selected.", "❌")
            return

        password = self.password_input.text()
        if not password:
            self.set_status("Enter a password first.", "❌")
            return

        try:
            decrypt_file(self.file_path, password)
            self.set_status("File decrypted successfully.", "✅")
        except Exception as e:
            self.set_status("Wrong password or corrupted file.", "❌")

    def set_status(self, message: str, icon: str):
        self.status.setText(message)
        self.status_icon.setText(icon)

    def apply_styles(self):
        self.setStyleSheet(
            """
            QWidget {
                background: #0f172a;
                color: #e2e8f0;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            #title {
                font-size: 22px;
                font-weight: 700;
                color: #f8fafc;
            }
            #subtitle {
                color: #cbd5e1;
                margin-bottom: 4px;
            }
            #fileLabel {
                padding: 10px 12px;
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QLineEdit {
                padding: 10px 12px;
                border-radius: 8px;
                border: 1px solid #334155;
                background: #0b1220;
                color: #e2e8f0;
            }
            QPushButton {
                padding: 10px 14px;
                border-radius: 8px;
                border: 1px solid #334155;
                background: #1d4ed8;
                color: #e2e8f0;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:pressed {
                background: #1e40af;
            }
            QPushButton#selectBtn {
                background: #0ea5e9;
            }
            #statusFrame {
                background: #0b1220;
                border: 1px solid #334155;
                border-radius: 10px;
            }
            QFrame[frameShape=\"4\"] { /* HLine */
                border: none;
                border-top: 1px solid #1e293b;
                margin: 4px 0 8px 0;
            }
            """
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileEncryptorApp()
    window.show()
    sys.exit(app.exec())
