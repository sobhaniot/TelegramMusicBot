import sys
from PyQt5.QtWidgets import QApplication
from src.B_Gui import MusicBotGui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MusicBotGui()
    gui.show()
    sys.exit(app.exec_())
