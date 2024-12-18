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
        
        #左侧：组件列表
        left_panel = self.create_left_panel()
        top_splitter.addWidget(left_panel)
        
        #右侧：画布区域
        self.scene = QtWidgets.QGraphicsScene()
        self.right_panel = QtWidgets.QGraphicsView(self.scene)
        self.right_panel.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        top_splitter.addWidget(self.right_panel)
        
        #设置分割器比例
        top_splitter.setSizes([150,650])
        
        main_layout.addWidget(top_splitter)
        
        self.show()
        
    def create_left_panel(self):
        #左侧面板用于显示组件列表
        left_pannel = QtWidgets.QListWidget()
        left_pannel.addItem("Pipe")
        left_pannel.addItem("Valve")
        left_pannel.addItem("Elbow")
        left_pannel.setMinimumWidth(150)
        return left_pannel
        
if __name__== "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = PressureDropCalculator()
    sys.exit(app.exec_())