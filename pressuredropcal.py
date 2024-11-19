from PyQt5 import QtWidgets, QtCore

class PressureDropCalculator(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        #设置主窗口标题和尺寸
        self.setWindowTitle("Pressure Drop Calculator")
        self.setGeometry(100,100,800,600)
        
        #设置中央部件和主布局
        central_widget = QtWidgets.QWidget(self)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        #创建顶部分割器
        top_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        
        
        
        main_layout.addWidget(top_splitter)
        
        self.show()
        
if __name__== "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = PressureDropCalculator()
    sys.exit(app.exec_())