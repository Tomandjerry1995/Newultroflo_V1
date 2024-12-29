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
        
        self.temp_line = None
        self.start_item = None
        

    # 放置组件        
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


    # 绘制连接线
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if event.button() == QtCore.Qt.MouseButton.LeftButton and isinstance(item, QtWidgets.QGraphicsEllipseItem) and item.data(QtCore.Qt.UserRole) == "right_point":
            self.start_item = item.parentItem()  # 记录起点组件
            self.temp_line = QtWidgets.QGraphicsPathItem()
            path = QtGui.QPainterPath()
            path.moveTo(item.sceneBoundingRect().center())
            self.temp_line.setPath(path)
            self.scene().addItem(self.temp_line)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_line:
            current_pos = self.mapToScene(event.pos())
            start_pos = self.start_item.right_point.sceneBoundingRect().center()
            path = QtGui.QPainterPath()
            path.moveTo(start_pos)
            path.lineTo(current_pos)
            self.temp_line.setPath(path)
        super().mouseMoveEvent(event)  
    
    def mouseReleaseEvent(self, event):
        if self.temp_line:
            # 获取鼠标释放位置下的所有图形项
            items = self.items(event.pos())
            end_item = None
            for item in items:
                if isinstance(item, QtWidgets.QGraphicsEllipseItem) and item.data(QtCore.Qt.UserRole) == "left_point":
                    end_item = item.parentItem()  # 获取终点组件
                    break
            if end_item and end_item != self.start_item:
                # 创建永久连接线
                connection = ConnectionLine(self.start_item, end_item)
                self.scene().addItem(connection)  # 添加到场景
                # 记录连接关系
                self.start_item.connections.append(connection)
                end_item.connections.append(connection)
                
                # 全局更新顺序
                self.update_order()
                
            # 移除临时线
            self.scene().removeItem(self.temp_line)
            self.temp_line = None
            self.start_item = None
        super().mouseReleaseEvent(event)

   
    def update_order(self):
        # 更新组件编号
        # 找到所有组件
        all_items = [item for item in self.scene().items() if isinstance(item, BaseComponent)]

        # 找到起点组件（没有被其他组件连接的组件）
        start_components = [item for item in all_items 
                            if not any(conn.end_item == item for conn in item.connections)]

        # 从起点开始递归更新顺序
        for start_component in start_components:
            self.propagate_order(start_component, 1)
            
    def propagate_order(self, component, order):
        # 强制更新顺序，不管是否发生变化
        component.set_order(order)  # 设置组件的顺序
        for connection in component.connections:
            # 确保检查连接线的起点是否是当前组件
            if connection.start_item == component:
                self.propagate_order(connection.end_item, order + 1)

                
                
                
class ConnectionLine(QtWidgets.QGraphicsPathItem):
    def __init__(self, start_item, end_item):
        super().__init__()
        self.start_item = start_item
        self.end_item = end_item
        self.setPen(QtGui.QPen(QtCore.Qt.black, 2))  # 设置线条样式
        self.update_connectionline()

    def update_connectionline(self):
        # 获取起点和终点的中心坐标
        start_pos = self.start_item.right_point.sceneBoundingRect().center()
        end_pos = self.end_item.left_point.sceneBoundingRect().center()
        # 创建路径
        path = QtGui.QPainterPath()
        path.moveTo(start_pos)
        # 添加控制点以创建平滑曲线
        control_point_1 = QtCore.QPointF(
            start_pos.x() + (end_pos.x() - start_pos.x()) / 2, start_pos.y()
        )
        control_point_2 = QtCore.QPointF(
            start_pos.x() + (end_pos.x() - start_pos.x()) / 2, end_pos.y()
        )
        path.cubicTo(control_point_1, control_point_2, end_pos)
        
        self.setPath(path)
    
    # 添加右键功能
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            menu = QtWidgets.QMenu()  # 创建右键菜单
            delete_action = menu.addAction("Delete Line")  # 添加删除选项
            action = menu.exec_(event.screenPos())  # 显示菜单并捕获选择
            if action == delete_action:
                self.delete_line()  # 调用删除方法
        super().mousePressEvent(event)
        
    
        
    # 删除连接线
    def delete_line(self):
        # 从组件中删除连接
        self.start_item.connections.remove(self)
        self.end_item.connections.remove(self)
        # 从场景中删除连接
        self.scene().removeItem(self)
        
    





if __name__== "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = PressureDropCalculator()
    sys.exit(app.exec_())