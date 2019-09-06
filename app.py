import sys  # sys нужен для передачи argv в QApplication
import json

from PyQt5 import QtWidgets, QtCore
from GUI import PyStrokeSideGUI  # Это наш конвертированный файл дизайна
from subprocess import Popen, PIPE


class ExampleApp(QtWidgets.QMainWindow, PyStrokeSideGUI.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # self.PySS = MasterSlavePyStrokeSide()

        self.process = Popen('python PyStrokeSide.py',
                             stdout=PIPE,
                             stdin=PIPE,
                             shell=True,
                             universal_newlines=True)


        self.btn_number_all_ergs.clicked.connect(lambda x: self.write({"erg_numeration": {"number_all_ergs": ""}}))
        self.btn_number_missing_ergs.clicked.connect(lambda x: self.write({"erg_numeration": {"number_missing_ergs": ""}}))
        self.btn_number_done.clicked.connect(lambda x: self.write({"erg_numeration": {"number_erg_done": ""}}))

    def write(self, cmd):
        cmd = json.dumps(cmd) + '\n'
        self.process.stdin.write(cmd)
        self.process.stdin.flush()



def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
