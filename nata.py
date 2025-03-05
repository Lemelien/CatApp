import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QTableWidget, QTableWidgetItem, 
                               QVBoxLayout, QHBoxLayout, QWidget, QComboBox, 
                               QPushButton, QDialog, QLineEdit, QFormLayout)

# Загрузка данных о котах из API
def load_cats():
    url = "https://api.thecatapi.com/v1/breeds"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

# Модальное окно для подробной информации
class CatDetailsDialog(QDialog):
    def __init__(self, cat, parent=None):
        super().__init__(parent)
        self.cat = cat
        self.setWindowTitle(f"Подробности о {cat.get('name', '')}")
        self.setModal(True)
        self.is_editable = False

        # Форма для отображения данных
        layout = QFormLayout()
        self.name_edit = QLineEdit(cat.get("name", ""))
        self.origin_edit = QLineEdit(cat.get("origin", ""))
        self.temperament_edit = QLineEdit(cat.get("temperament", ""))
        self.description_edit = QLineEdit(cat.get("description", ""))
        self.life_span_edit = QLineEdit(cat.get("life_span", ""))

        self.set_fields_read_only(True)

        layout.addRow("Имя:", self.name_edit)
        layout.addRow("Происхождение:", self.origin_edit)
        layout.addRow("Темперамент:", self.temperament_edit)
        layout.addRow("Описание:", self.description_edit)
        layout.addRow("Продолжительность жизни:", self.life_span_edit)

        # Кнопки
        self.edit_button = QPushButton("Редактировать")
        self.save_button = QPushButton("Сохранить")
        self.save_button.setEnabled(False)
        layout.addRow(self.edit_button)
        layout.addRow(self.save_button)

        self.edit_button.clicked.connect(self.toggle_edit)
        self.save_button.clicked.connect(self.save_changes)

        self.setLayout(layout)

    def set_fields_read_only(self, read_only):
        self.name_edit.setReadOnly(read_only)
        self.origin_edit.setReadOnly(read_only)
        self.temperament_edit.setReadOnly(read_only)
        self.description_edit.setReadOnly(read_only)
        self.life_span_edit.setReadOnly(read_only)

    def toggle_edit(self):
        self.is_editable = not self.is_editable
        self.set_fields_read_only(not self.is_editable)
        self.edit_button.setText("Отменить" if self.is_editable else "Редактировать")
        self.save_button.setEnabled(self.is_editable)

    def save_changes(self):
        self.cat["name"] = self.name_edit.text()
        self.cat["origin"] = self.origin_edit.text()
        self.cat["temperament"] = self.temperament_edit.text()
        self.cat["description"] = self.description_edit.text()
        self.cat["life_span"] = self.life_span_edit.text()
        self.toggle_edit()
        self.parent().update_table()

# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Котики")
        self.setGeometry(100, 100, 800, 600)

        # Загрузка данных
        self.cats = load_cats()

        # Основной виджет и layout
        widget = QWidget()
        self.layout_v = QVBoxLayout()
        widget.setLayout(self.layout_v)
        self.setCentralWidget(widget)

        # Выпадающий список для фильтрации
        self.origin_filter = QComboBox()
        self.origin_filter.addItem("Все страны")
        origins = sorted(set(cat.get("origin", "") for cat in self.cats))
        self.origin_filter.addItems(origins)
        self.origin_filter.currentTextChanged.connect(self.filter_table)
        self.layout_v.addWidget(self.origin_filter)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Имя", "Происхождение", "Темперамент"])
        self.update_table()
        self.table.doubleClicked.connect(self.show_details)
        self.layout_v.addWidget(self.table)

        # Кнопка удаления
        self.delete_button = QPushButton("Удалить выбранного кота")
        self.delete_button.clicked.connect(self.delete_cat)
        self.layout_v.addWidget(self.delete_button)

    def update_table(self):
        filtered_cats = self.get_filtered_cats()
        self.table.setRowCount(len(filtered_cats))
        for row, cat in enumerate(filtered_cats):
            self.table.setItem(row, 0, QTableWidgetItem(cat.get("name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(cat.get("origin", "")))
            self.table.setItem(row, 2, QTableWidgetItem(cat.get("temperament", "")))
        self.table.resizeColumnsToContents()

    def get_filtered_cats(self):
        selected_origin = self.origin_filter.currentText()
        if selected_origin == "Все страны":
            return self.cats
        return [cat for cat in self.cats if cat.get("origin", "") == selected_origin]

    def show_details(self):
        row = self.table.currentRow()
        if row >= 0:
            cat = self.get_filtered_cats()[row]
            dialog = CatDetailsDialog(cat, self)
            dialog.exec_()

    def filter_table(self):
        self.update_table()

    def delete_cat(self):
        row = self.table.currentRow()
        if row >= 0:
            filtered_cats = self.get_filtered_cats()
            cat_to_remove = filtered_cats[row]
            self.cats.remove(cat_to_remove)
            self.update_table()