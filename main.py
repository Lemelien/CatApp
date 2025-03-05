
from PySide6.QtWidgets import QApplication 
from nata import MainWindow 


# Запуск приложения
app = QApplication([])
window = MainWindow()
window.show()
app.exec()