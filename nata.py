import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QTableWidget, QTableWidgetItem, 
                               QVBoxLayout, QHBoxLayout, QWidget, QComboBox, 
                               QPushButton, QDialog, QLineEdit, QFormLayout)

# Загрузка данных о котах из API
def загрузить_котов():
    адрес = "https://api.thecatapi.com/v1/breeds"
    ответ = requests.get(адрес)
    if ответ.status_code == 200:
        return ответ.json()
    return []

# Модальное окно для подробной информации о коте
class ОкноПодробностейКота(QDialog):
    def __init__(self, кот, родитель=None):
        super().__init__(родитель)
        self.кот = кот
        self.setWindowTitle(f"Подробности о {кот.get('name', '')}")
        self.setModal(True)
        self.редактируемое = False

        # Форма для отображения данных
        макет = QFormLayout()
        self.поле_имя = QLineEdit(кот.get("name", ""))
        self.поле_происхождение = QLineEdit(кот.get("origin", ""))
        self.поле_темперамент = QLineEdit(кот.get("temperament", ""))
        self.поле_описание = QLineEdit(кот.get("description", ""))
        self.поле_жизнь = QLineEdit(кот.get("life_span", ""))

        self.установить_только_чтение(True)

        макет.addRow("Имя:", self.поле_имя)
        макет.addRow("Происхождение:", self.поле_происхождение)
        макет.addRow("Темперамент:", self.поле_темперамент)
        макет.addRow("Описание:", self.поле_описание)
        макет.addRow("Продолжительность жизни:", self.поле_жизнь)

        # Кнопки
        self.кнопка_редактировать = QPushButton("Редактировать")
        self.кнопка_сохранить = QPushButton("Сохранить")
        self.кнопка_сохранить.setEnabled(False)
        макет.addRow(self.кнопка_редактировать)
        макет.addRow(self.кнопка_сохранить)

        self.кнопка_редактировать.clicked.connect(self.переключить_редактирование)
        self.кнопка_сохранить.clicked.connect(self.сохранить_изменения)

        self.setLayout(макет)

    def установить_только_чтение(self, только_чтение):
        self.поле_имя.setReadOnly(только_чтение)
        self.поле_происхождение.setReadOnly(только_чтение)
        self.поле_темперамент.setReadOnly(только_чтение)
        self.поле_описание.setReadOnly(только_чтение)
        self.поле_жизнь.setReadOnly(только_чтение)

    def переключить_редактирование(self):
        self.редактируемое = not self.редактируемое
        self.установить_только_чтение(not self.редактируемое)
        self.кнопка_редактировать.setText("Отменить" if self.редактируемое else "Редактировать")
        self.кнопка_сохранить.setEnabled(self.редактируемое)

    def сохранить_изменения(self):
        self.кот["name"] = self.поле_имя.text()
        self.кот["origin"] = self.поле_происхождение.text()
        self.кот["temperament"] = self.поле_темперамент.text()
        self.кот["description"] = self.поле_описание.text()
        self.кот["life_span"] = self.поле_жизнь.text()
        self.переключить_редактирование()
        self.parent().обновить_таблицу()

# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Котики")
        self.setGeometry(100, 100, 800, 600)

        # Загрузка данных
        self.коты = загрузить_котов()

        # Основной виджет и вертикальный макет
        виджет = QWidget()
        self.вертикальный_макет = QVBoxLayout()
        виджет.setLayout(self.вертикальный_макет)
        self.setCentralWidget(виджет)

        # Выпадающий список для фильтрации
        self.фильтр_происхождения = QComboBox()
        self.фильтр_происхождения.addItem("Все страны")
        происхождения = sorted(set(кот.get("origin", "") for кот in self.коты))
        self.фильтр_происхождения.addItems(происхождения)
        self.фильтр_происхождения.currentTextChanged.connect(self.отфильтровать_таблицу)
        self.вертикальный_макет.addWidget(self.фильтр_происхождения)

        # Таблица
        self.таблица = QTableWidget()
        self.таблица.setColumnCount(3)
        self.таблица.setHorizontalHeaderLabels(["Имя", "Происхождение", "Темперамент"])
        self.обновить_таблицу()
        self.таблица.doubleClicked.connect(self.показать_подробности)
        self.вертикальный_макет.addWidget(self.таблица)

        # Кнопка удаления
        self.кнопка_удалить = QPushButton("Удалить выбранного кота")
        self.кнопка_удалить.clicked.connect(self.удалить_кота)
        self.вертикальный_макет.addWidget(self.кнопка_удалить)

    def обновить_таблицу(self):
        отфильтрованные_коты = self.получить_отфильтрованных_котов()
        self.таблица.setRowCount(len(отфильтрованные_коты))
        for строка, кот in enumerate(отфильтрованные_коты):
            self.таблица.setItem(строка, 0, QTableWidgetItem(кот.get("name", "")))
            self.таблица.setItem(строка, 1, QTableWidgetItem(кот.get("origin", "")))
            self.таблица.setItem(строка, 2, QTableWidgetItem(кот.get("temperament", "")))
        self.таблица.resizeColumnsToContents()

    def получить_отфильтрованных_котов(self):
        выбранное_происхождение = self.фильтр_происхождения.currentText()
        if выбранное_происхождение == "Все страны":
            return self.коты
        return [кот for кот in self.коты if кот.get("origin", "") == выбранное_происхождение]

    def показать_подробности(self):
        строка = self.таблица.currentRow()
        if строка >= 0:
            кот = self.получить_отфильтрованных_котов()[строка]
            диалог = ОкноПодробностейКота(кот, self)
            диалог.exec_()

    def отфильтровать_таблицу(self):
        self.обновить_таблицу()

    def удалить_кота(self):
        строка = self.таблица.currentRow()
        if строка >= 0:
            отфильтрованные_коты = self.получить_отфильтрованных_котов()
            кот_для_удаления = отфильтрованные_коты[строка]
            self.коты.remove(кот_для_удаления)
            self.обновить_таблицу()
