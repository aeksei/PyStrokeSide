import sys  # sys нужен для передачи argv в QApplication
import json

from PyQt5 import QtWidgets, QtCore
from GUI import PyStrokeSideGUI    # Это наш конвертированный файл дизайна
from MasterSlavePyStrokeSide import MasterSlavePyStrokeSide


class ExampleApp(QtWidgets.QMainWindow, PyStrokeSideGUI.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.PySS = MasterSlavePyStrokeSide()

        self.btn_number_all_ergs.clicked.connect(self.PySS.number_all_erg())


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

    window.PySS.restore_erg()


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
