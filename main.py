import sys
import argparse
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from wavoscope.gui.main_window import MainWindow
from wavoscope.gui.colours import load_palette
from PySide6.QtGui import QPalette, QColor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug-latency", action="store_true",
                        help="Show playback-line latency overlay")
    cli_args, _ = parser.parse_known_args()

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
    window = MainWindow(debug_latency=cli_args.debug_latency)
    app.setWindowIcon(QIcon(f"./wavoscope/resources/icons/app-icon.svg"))
    window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()