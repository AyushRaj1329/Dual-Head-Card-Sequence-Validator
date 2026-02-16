# src/ui/main_application.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QGraphicsOpacityEffect, QSizePolicy, QScrollArea, QMessageBox, QButtonGroup
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QParallelAnimationGroup, QTimer
from PyQt6.QtGui import QPixmap, QScreen

from ..app_state import AppState
from .network_setup_dual import NetworkSetupWindow
from .file_management_dual import FileManagementWindow
from .scanner_logging_dual import ScannerLoggingDualWindow
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget, ScalableLabel
import constants

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class HomePage(QMainWindow):
    def __init__(self, dual_head_manager):
        super().__init__()
        self.dual_head_manager = dual_head_manager
        self.head_a = dual_head_manager.head_a
        self.head_b = dual_head_manager.head_b
        self.setWindowTitle("Card Sequence Validation System - Dual Head")

        self.com_port_window = None
        self.file_management_window = None
        self.scanner_logging_window = None
        self.initializing_label = None
        self.animation_played = False

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        central_widget = QWidget()
        scroll_area.setWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(30)

        # Create the logo for animation
        self.logo_label = ScalableLabel(self)
        self.aspect_ratio = 16/9
        logo_path = resource_path(constants.LOGO_PATH)
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.aspect_ratio = pixmap.width() / pixmap.height()
            self.logo_label.setPixmap(pixmap)

        # Create all widgets but keep them hidden initially
        self.header_container = QWidget()
        self.welcome_section = QWidget()
        self.feature_cards_container = QWidget()
        self.system_status_container = QWidget()

        self.create_header(self.header_container)
        self.create_welcome_section(self.welcome_section)
        self.create_feature_cards(self.feature_cards_container)
        self.create_system_status(self.system_status_container)

        self.main_layout.addWidget(self.header_container)
        self.main_layout.addWidget(self.welcome_section)
        self.main_layout.addWidget(self.feature_cards_container)
        self.main_layout.addWidget(self.system_status_container)
        self.main_layout.addStretch()

        self.widgets_to_fade_in = [self.header_container, self.welcome_section, self.feature_cards_container, self.system_status_container]
        for widget in self.widgets_to_fade_in:
            opacity_effect = QGraphicsOpacityEffect(opacity=0.0)
            widget.setGraphicsEffect(opacity_effect)
            widget.setAutoFillBackground(True)

        # Connect signals from both heads
        self.head_a.state_changed.connect(self.update_status_indicators)
        self.head_b.state_changed.connect(self.update_status_indicators)
        self.head_a.output_com_status_changed.connect(lambda msg, color: self.update_output_port_status('A', msg, color))
        self.head_b.output_com_status_changed.connect(lambda msg, color: self.update_output_port_status('B', msg, color))
        
        self.update_status_indicators()

        # Apply initial theme from Head A (both heads share theme)
        self.apply_theme(self.head_a.current_theme)

        # Perform license validation
        self.check_license()

    def check_license(self):
        from src.services.licensing import validate_license
        is_valid, message, machine_id = validate_license()

        if not is_valid:
            error_message = f"{message}\n\nPlease contact support to obtain a valid license."
            QMessageBox.critical(self, "License Error", error_message)
            sys.exit(1)

    def showEvent(self, event):
        super().showEvent(event)

        if not self.animation_played:
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()

            # Make initial logo size responsive to screen height
            start_height = int(screen_geometry.height() * 0.3)
            start_width = int(start_height * self.aspect_ratio)

            # Center the logo on the screen
            x = (screen_geometry.width() - start_width) // 2
            y = (screen_geometry.height() - start_height) // 2

            self.logo_label.setGeometry(x, y, start_width, start_height)
            self.logo_label.raise_()

            # Create and position the initializing label
            self.initializing_label = QLabel("Initializing...", self)
            self.initializing_label.setObjectName("subtitle")
            self.initializing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.initializing_label.adjustSize()
            label_x = x + (start_width - self.initializing_label.width()) // 2
            label_y = y + start_height + 10
            self.initializing_label.setGeometry(label_x, label_y, self.initializing_label.width(), self.initializing_label.height())
            self.initializing_label.raise_()

            # Delay the start of the animation
            QTimer.singleShot(1500, self.start_animation)
            self.animation_played = True

    

    def update_animation_end_rect(self):
        # Final state of the logo, calculated dynamically
        end_rect = self.header_logo_placeholder.geometry()
        # Map the position from the header_container's coordinate system to the main window's
        global_pos = self.header_logo_placeholder.parentWidget().mapTo(self, self.header_logo_placeholder.pos())
        end_rect.moveTo(global_pos)
        self.animation_end_rect = end_rect

    def update_animation_end_rect(self):
        # Final state of the logo, calculated dynamically
        end_rect = self.header_logo_placeholder.geometry()
        # Map the position from the header_container's coordinate system to the main window's
        global_pos = self.header_logo_placeholder.parentWidget().mapTo(self, self.header_logo_placeholder.pos())
        end_rect.moveTo(global_pos)
        self.animation_end_rect = end_rect

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # If the animation is in progress, update its end value
        if self.animation_played and hasattr(self, 'logo_animation') and self.logo_animation.state() == QPropertyAnimation.State.Running:
            self.update_animation_end_rect()
            self.logo_animation.setEndValue(self.animation_end_rect)
        # If the animation is in progress, update its end value
        if self.animation_played and hasattr(self, 'logo_animation') and self.logo_animation.state() == QPropertyAnimation.State.Running:
            self.update_animation_end_rect()
            self.logo_animation.setEndValue(self.animation_end_rect)

    def start_animation(self):
        self.update_animation_end_rect()  # Set the final position

        start_rect = self.logo_label.geometry()

        # Animation for the logo
        self.logo_animation = QPropertyAnimation(self.logo_label, b"geometry")
        self.logo_animation.setDuration(2500)
        self.logo_animation.setStartValue(start_rect)
        self.logo_animation.setEndValue(self.animation_end_rect)
        self.logo_animation.setEasingCurve(QEasingCurve.Type.OutQuint)

        # Animations for fading in the other widgets
        self.fade_in_animations = QParallelAnimationGroup()
        for widget in self.widgets_to_fade_in:
            animation = QPropertyAnimation(widget.graphicsEffect(), b"opacity")
            animation.setDuration(2000)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            self.fade_in_animations.addAnimation(animation)

        # Start animations
        self.logo_animation.start()
        self.fade_in_animations.start()

    def fade_out_initializing_label(self):
        if self.initializing_label:
            # Fade out the initializing label
            fade_out_animation = QPropertyAnimation(self.initializing_label, b"windowOpacity")
            fade_out_animation.setDuration(500) # Faster fade out
            fade_out_animation.setStartValue(1.0)
            fade_out_animation.setEndValue(0.0)
            fade_out_animation.start()

    def create_header(self, container):
        header_layout = QHBoxLayout(container)
        header_layout.setContentsMargins(0, 0, 0, 10)
        header_layout.setSpacing(15)

        self.header_logo_placeholder = ScalableLabel()
        self.header_logo_placeholder.setMinimumWidth(100) # Prevent from becoming too small
        self.header_logo_placeholder.setMaximumHeight(120)  # Max height for the logo

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        title = QLabel("Card Sequence Validator - Dual Head")
        title.setObjectName("mainTitle")
        subtitle = QLabel("Automated Quality Control - Head A & Head B")
        subtitle.setObjectName("mainSubtitle")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        clock = ClockWidget()

        # Theme Toggle Button
        self.theme_button = QPushButton()
        self.theme_button.clicked.connect(self.toggle_theme)
        self.update_theme_button_text(self.head_a.current_theme)

        header_layout.addWidget(self.header_logo_placeholder, 0)
        header_layout.addLayout(title_layout, 1)
        header_layout.addStretch()
        header_layout.addWidget(clock)
        header_layout.addWidget(self.theme_button)

    def update_theme_button_text(self, theme_name):
        if theme_name == "dark":
            self.theme_button.setText("Light Mode")
            self.theme_button.setObjectName("light_theme_toggle")
        else:
            self.theme_button.setText("Dark Mode")
            self.theme_button.setObjectName("dark_theme_toggle")
        self.theme_button.style().unpolish(self.theme_button)
        self.theme_button.style().polish(self.theme_button)

    def create_welcome_section(self, container):
        layout = QVBoxLayout(container)
        welcome_frame = QFrame()
        welcome_frame.setObjectName("accentPanel")
        welcome_layout = QVBoxLayout(welcome_frame)
        welcome_layout.setSpacing(10)
        welcome_layout.setContentsMargins(30, 30, 30, 30)

        welcome_title = QLabel("Welcome to the Validation Control Panel")
        welcome_title.setObjectName("h2")
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_desc = QLabel("Configure hardware, manage test sequences, and monitor validation processes.")
        welcome_desc.setObjectName("subtitle")
        welcome_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_desc)
        layout.addWidget(welcome_frame)

    def create_feature_cards(self, container):
        layout = QHBoxLayout(container)
        layout.setSpacing(30)
        cards_data = [
            ("Scanner & Logging", "Live scanner input and validation logging", "Scanner Control", "📱", self.open_scanner),
            ("Network & COM Setup", "Configure network and serial connections", "Configuration", "🔧", self.open_com_port_setup),
            ("File Management", "Manage card sequence files and logs", "File & Log Management", "📁", self.open_file_management)
        ]
        for title, desc, btn_text, icon, callback in cards_data:
            layout.addWidget(self.create_feature_card(title, desc, btn_text, icon, callback), 1)

    def create_feature_card(self, title, description, button_text, icon, callback):
        card = QFrame()
        card.setObjectName("panel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("h2")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel(description)
        desc_label.setObjectName("subtitle")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)

        button = QPushButton(button_text)
        button.setObjectName("primary")
        button.clicked.connect(callback)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(button)
        return card

    def create_system_status(self, container):
        layout = QVBoxLayout(container)
        status_frame = QFrame()
        status_frame.setObjectName("panel")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(25, 20, 25, 20)
        status_title = QLabel("System Status - Dual Head Operation")
        status_title.setObjectName("h2")

        # Create two rows: one for Head A, one for Head B
        main_indicators_layout = QVBoxLayout()
        main_indicators_layout.setSpacing(20)
        
        # Head A Status Row
        head_a_label = QLabel("Head A (Right)")
        head_a_label.setObjectName("h2")
        head_a_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        main_indicators_layout.addWidget(head_a_label)
        
        head_a_indicators = QHBoxLayout()
        head_a_indicators.setSpacing(30)
        
        self.scanner_status_label_a = QLabel()
        self.file_status_label_a = QLabel()
        self.com_status_label_a = QLabel()
        self.output_com_status_label_a = QLabel()
        self.scan_card_com_status_label_a = QLabel()

        head_a_indicators.addWidget(self.create_status_indicator("Scanner:", self.scanner_status_label_a), 1)
        head_a_indicators.addWidget(self.create_status_indicator("Input Port:", self.com_status_label_a), 1)
        head_a_indicators.addWidget(self.create_status_indicator("Output Port:", self.output_com_status_label_a), 1)
        head_a_indicators.addWidget(self.create_status_indicator("Scan Card Port:", self.scan_card_com_status_label_a), 1)
        head_a_indicators.addWidget(self.create_status_indicator("File Loaded:", self.file_status_label_a), 1)
        
        main_indicators_layout.addLayout(head_a_indicators)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #444; margin: 10px 0;")
        main_indicators_layout.addWidget(separator)
        
        # Head B Status Row
        head_b_label = QLabel("Head B (Left)")
        head_b_label.setObjectName("h2")
        head_b_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        main_indicators_layout.addWidget(head_b_label)
        
        head_b_indicators = QHBoxLayout()
        head_b_indicators.setSpacing(30)
        
        self.scanner_status_label_b = QLabel()
        self.file_status_label_b = QLabel()
        self.com_status_label_b = QLabel()
        self.output_com_status_label_b = QLabel()
        self.scan_card_com_status_label_b = QLabel()

        head_b_indicators.addWidget(self.create_status_indicator("Scanner:", self.scanner_status_label_b), 1)
        head_b_indicators.addWidget(self.create_status_indicator("Input Port:", self.com_status_label_b), 1)
        head_b_indicators.addWidget(self.create_status_indicator("Output Port:", self.output_com_status_label_b), 1)
        head_b_indicators.addWidget(self.create_status_indicator("Scan Card Port:", self.scan_card_com_status_label_b), 1)
        head_b_indicators.addWidget(self.create_status_indicator("File Loaded:", self.file_status_label_b), 1)
        
        main_indicators_layout.addLayout(head_b_indicators)

        status_layout.addWidget(status_title)
        status_layout.addLayout(main_indicators_layout)
        layout.addWidget(status_frame)

    def create_status_indicator(self, label_text, status_widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        label = QLabel(label_text)
        label.setObjectName("h2")
        layout.addWidget(label)
        layout.addWidget(status_widget)
        return container

    def update_status_indicators(self):
        # Update Head A status
        if self.head_a.is_scanning:
            self.scanner_status_label_a.setText("Scanning")
            self.scanner_status_label_a.setObjectName("statusOK")
        else:
            self.scanner_status_label_a.setText("Idle")
            self.scanner_status_label_a.setObjectName("statusIdle")

        if self.head_a.selected_file_path:
            file_name = os.path.basename(self.head_a.selected_file_path)
            self.file_status_label_a.setText(f"{file_name} ({len(self.head_a.expected_cards)} cards)")
            self.file_status_label_a.setObjectName("statusOK")
        else:
            self.file_status_label_a.setText("No File")
            self.file_status_label_a.setObjectName("statusWarning")

        if self.head_a.main_scanner_config:
            config = self.head_a.main_scanner_config
            self.com_status_label_a.setText(f"{config['local_ip']}:{config['local_port']}")
            self.com_status_label_a.setObjectName("statusOK")
        else:
            self.com_status_label_a.setText("Not Set")
            self.com_status_label_a.setObjectName("statusWarning")

        if self.head_a.output_config:
            config = self.head_a.output_config
            self.output_com_status_label_a.setText(f"{config['remote_ip']}:{config['remote_port']}")
            self.output_com_status_label_a.setObjectName("statusOK")
        else:
            self.output_com_status_label_a.setText("Not Set")
            self.output_com_status_label_a.setObjectName("statusWarning")

        if self.head_a.ondemand_scanner_config:
            config = self.head_a.ondemand_scanner_config
            self.scan_card_com_status_label_a.setText(f"{config['local_ip']}:{config['local_port']}")
            self.scan_card_com_status_label_a.setObjectName("statusOK")
        else:
            self.scan_card_com_status_label_a.setText("Not Set")
            self.scan_card_com_status_label_a.setObjectName("statusWarning")

        # Update Head B status
        if self.head_b.is_scanning:
            self.scanner_status_label_b.setText("Scanning")
            self.scanner_status_label_b.setObjectName("statusOK")
        else:
            self.scanner_status_label_b.setText("Idle")
            self.scanner_status_label_b.setObjectName("statusIdle")

        if self.head_b.selected_file_path:
            file_name = os.path.basename(self.head_b.selected_file_path)
            self.file_status_label_b.setText(f"{file_name} ({len(self.head_b.expected_cards)} cards)")
            self.file_status_label_b.setObjectName("statusOK")
        else:
            self.file_status_label_b.setText("No File")
            self.file_status_label_b.setObjectName("statusWarning")

        if self.head_b.main_scanner_config:
            config = self.head_b.main_scanner_config
            self.com_status_label_b.setText(f"{config['local_ip']}:{config['local_port']}")
            self.com_status_label_b.setObjectName("statusOK")
        else:
            self.com_status_label_b.setText("Not Set")
            self.com_status_label_b.setObjectName("statusWarning")

        if self.head_b.output_config:
            config = self.head_b.output_config
            self.output_com_status_label_b.setText(f"{config['remote_ip']}:{config['remote_port']}")
            self.output_com_status_label_b.setObjectName("statusOK")
        else:
            self.output_com_status_label_b.setText("Not Set")
            self.output_com_status_label_b.setObjectName("statusWarning")

        if self.head_b.ondemand_scanner_config:
            config = self.head_b.ondemand_scanner_config
            self.scan_card_com_status_label_b.setText(f"{config['local_ip']}:{config['local_port']}")
            self.scan_card_com_status_label_b.setObjectName("statusOK")
        else:
            self.scan_card_com_status_label_b.setText("Not Set")
            self.scan_card_com_status_label_b.setObjectName("statusWarning")

        # Re-polish all status labels
        for label in [self.scanner_status_label_a, self.file_status_label_a, self.com_status_label_a,
                     self.output_com_status_label_a, self.scan_card_com_status_label_a,
                     self.scanner_status_label_b, self.file_status_label_b, self.com_status_label_b,
                     self.output_com_status_label_b, self.scan_card_com_status_label_b]:
            label.style().unpolish(label)
            label.style().polish(label)

    def update_output_port_status(self, head_id, message, color):
        """Update output port status in real-time for specified head"""
        if head_id == 'A':
            head = self.head_a
            label = self.output_com_status_label_a
        else:
            head = self.head_b
            label = self.output_com_status_label_b
            
        if head.output_config:
            config = head.output_config
            label.setText(f"{config['remote_ip']}:{config['remote_port']}")
            label.setObjectName("statusOK")
        elif "Not Connected" in message or "Not Set" in message:
            label.setText("Not Set")
            label.setObjectName("statusWarning")
        else:
            label.setText("Error")
            label.setObjectName("statusError")
        
        label.style().unpolish(label)
        label.style().polish(label)

    def open_scanner(self):
        if self.scanner_logging_window is None:
            self.scanner_logging_window = ScannerLoggingDualWindow(self.dual_head_manager)
        if self.scanner_logging_window.isMinimized():
            self.scanner_logging_window.showNormal()
        self.scanner_logging_window.showMaximized()
        self.scanner_logging_window.raise_()
        self.scanner_logging_window.activateWindow()

    def open_com_port_setup(self):
        if self.com_port_window is None:
            self.com_port_window = NetworkSetupWindow(self.dual_head_manager)
        if self.com_port_window.isMinimized():
            self.com_port_window.showNormal()
        self.com_port_window.showMaximized()
        self.com_port_window.raise_()
        self.com_port_window.activateWindow()

    def open_file_management(self):
        if self.file_management_window is None:
            self.file_management_window = FileManagementWindow(self.dual_head_manager, self.open_scanner)
        if self.file_management_window.isMinimized():
            self.file_management_window.showNormal()
        self.file_management_window.showMaximized()
        self.file_management_window.raise_()
        self.file_management_window.activateWindow()

    def closeEvent(self, event):
        self.dual_head_manager.stop_all_scanning()
        self.dual_head_manager.save_all()
        QApplication.quit()

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.theme_button.setText("Dark Mode")
            self.theme_button.setObjectName("dark_theme_toggle")
        else:
            self.current_theme = "dark"
            self.theme_button.setText("Light Mode")
            self.theme_button.setObjectName("light_theme_toggle")

        self.apply_theme(self.current_theme)
        # Save theme to both heads
        self.head_a.set_theme(self.current_theme)
        self.head_b.set_theme(self.current_theme)

    def apply_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)
        self.current_theme = theme_name
        # Re-polish all widgets to apply new stylesheet
        for widget in QApplication.allWidgets():
            widget.style().unpolish(widget)
            widget.style().polish(widget)