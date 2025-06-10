from PyQt5.QtWidgets import QApplication
import sys
from ui_main import GeoGebraApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = GeoGebraApp()
    ventana.show()
    sys.exit(app.exec_())
