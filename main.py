from PyQt5 import QtWidgets, QtCore, QtGui
from components import *  # 导入组件类

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
        self.right_panel = CustomGraphicsView(self.scene, self)
        self.right_panel.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        top_splitter.addWidget(self.right_panel)
        
        #设置分割器比例
        top_splitter.setSizes([150,650])
        
        main_layout.addWidget(top_splitter)
        
        self.show()
        
    def create_left_panel(self):
        # 左侧面板用于显示组件列表及其图标
        left_panel = QtWidgets.QListWidget()
        left_panel.setViewMode(QtWidgets.QListView.ViewMode.ListMode)
        left_panel.setIconSize(QtCore.QSize(48,48)) #设置图标大小
        left_panel.setSpacing(10) #设置组件间距
        left_panel.setMovement(QtWidgets.QListView.Movement.Static)
        
        # 定义组件和对应的图标
        components = [
            ("Pipe", "assets/pipe.png"),
            ("Valve", "assets/valve.png"),
            ("Elbow", "assets/elbow.png"),
            ("Reducer", "assets/reducer.png"),
            ("Tee", "assets/tee.png"),
            ("Inlet", "assets/inlet.png"),
            ("Outlet", "assets/outlet.png")            
        ]
        
        # 创建组件列表项
        for name, icon_path in components:
            item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path), name)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, icon_path)
            left_panel.addItem(item)
        
        left_panel.setMinimumWidth(150)
        left_panel.setDragEnabled(True) # 启用拖拽
        left_panel.setObjectName("componentList")
        left_panel.itemPressed.connect(self.start_drag)
        return left_panel
             
    def start_drag(self, item):
        selected_item = item # 获取选中的列表项
        if selected_item:
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText(selected_item.text())
            mime_data.setData("application/x-icon-path", selected_item.data(QtCore.Qt.ItemDataRole.UserRole).encode())
            drag.setMimeData(mime_data)
            drag.setPixmap(selected_item.icon().pixmap(48, 48))
            drag.setHotSpot(QtCore.QPoint(drag.pixmap().width() // 2, drag.pixmap().height() // 2))
            drag.exec_(QtCore.Qt.DropAction.MoveAction)
        

class CustomGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, scene, main_window, parent=None):
        super().__init__(scene, parent)
        self.main_window = main_window
        self.setAcceptDrops(True) # 允许放置事件

        
    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()
    
    def dropEvent(self, event):
        # 获取图标路径
        icon_path = event.mimeData().data("application/x-icon-path").data().decode()

        # 提取组件类型（根据文件名确定）
        component_type = icon_path.split('/')[-1].split('.')[0].capitalize()

        # 映射组件类型到具体类
        component_mapping = {
            "Pipe": PipeComponent,
            "Inlet": InletComponent,
            "Valve": ValveComponent,
            "Elbow": ElbowComponent,
            "Reducer": ReducerComponent,
            "Tee": TeeComponent,
            "Outlet": OutletComponent
        }
        # 获取组件类，默认使用 BaseComponent
        component_class = component_mapping.get(component_type, BaseComponent)

        # 创建组件实例
        component = component_class(icon_path)

        # 设置组件的位置并添加到场景
        drop_position = self.mapToScene(event.pos())
        component.setPos(drop_position)
        self.scene().addItem(component)

        # 接受放置动作
        event.acceptProposedAction()

        
        



        
if __name__== "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = PressureDropCalculator()
    sys.exit(app.exec_())