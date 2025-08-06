import sys
from PySide6.QtWidgets import QApplication
from wavoscope.gui.main_window import MainWindow
from wavoscope.gui.colours import load_palette
from PySide6.QtGui import QPalette, QColor

def main():
    app = QApplication(sys.argv)

    palette = load_palette("dark")
    qpal = QPalette()
    qpal.setColor(QPalette.Window, QColor(palette["background"]))
    qpal.setColor(QPalette.WindowText, QColor(palette["text"]))
    qpal.setColor(QPalette.Base, QColor(palette["background"]))
    qpal.setColor(QPalette.AlternateBase, QColor(palette["background"]))
    qpal.setColor(QPalette.Text, QColor(palette["text"]))
    qpal.setColor(QPalette.Button, QColor(palette["background"]))
    qpal.setColor(QPalette.ButtonText, QColor(palette["text"]))
    app.setPalette(qpal)

    app.setApplicationName("Wavoscope")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())