from PyQt5 import QtWidgets, QtCore, QtGui

class BaseComponent(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, icon_path, component_type):
        super().__init__()
        # 设置组件的图标
        self.setPixmap(QtGui.QPixmap(icon_path).scaled(40, 40, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        self.setFlags(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        # 基础属性
        self.component_type = component_type
        self.connections = [] # 存储连接的线条
        self.add_connection_points()
        self.order = None # 顺序编号

        

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.show_input_dialog()

    def show_input_dialog(self):
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(f"{self.component_type} Parameters")

        # 动态生成输入字段
        layout = QtWidgets.QFormLayout(dialog)
        for name, value in self.get_parameters().items():
            input_field = QtWidgets.QLineEdit(str(value))
            layout.addRow(f"{name}:", input_field)
            setattr(self, f"{name}_input", input_field)

        # 添加按钮
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            self.update_parameters_from_inputs()

    # 添加连接线
    def add_connection_points(self):
        # 添加左连接点
        self.left_point = QtWidgets.QGraphicsEllipseItem(-10, self.pixmap().height() / 2 - 5, 10, 10, self)
        self.left_point.setBrush(QtGui.QBrush(QtCore.Qt.red))
        self.left_point.setPen(QtGui.QPen(QtCore.Qt.red, 2))
        self.left_point.setZValue(self.zValue() + 1)
        self.left_point.setData(QtCore.Qt.UserRole, "left_point")  # 添加标识

        # 添加右连接点
        self.right_point = QtWidgets.QGraphicsEllipseItem(self.pixmap().width(), self.pixmap().height() / 2 - 5, 10, 10, self)
        self.right_point.setBrush(QtGui.QBrush(QtCore.Qt.red))
        self.right_point.setPen(QtGui.QPen(QtCore.Qt.red, 2))
        self.right_point.setZValue(self.zValue() + 1)
        self.right_point.setData(QtCore.Qt.UserRole, "right_point")  # 添加标识

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # 位置变化，更新连接线位置
            for connection in self.connections:
                connection.update_position()
        return super().itemChange(change, value)

    # 添加次序
    def set_order(self, order):
        self.order = order
        self.update()   # 触发重绘以显示顺序

    def paint(self, painter, option, widget = None):
        super().paint(painter, option, widget)
        if self.order is not None:
            painter.setPen(QtGui.QPen(QtCore.Qt.black))
            painter.setFont(QtGui.QFont("Arial", 10))
            painter.drawText(self.boundingRect(), QtCore.Qt.AlignCenter, str(self.order))




    def get_parameters(self):
        """在具体组件中实现，返回参数字典"""
        return {}

    def update_parameters_from_inputs(self):
        """更新参数，具体逻辑由子类实现"""
        pass











class PipeComponent(BaseComponent):
    def __init__(self, icon_path):
        super().__init__(icon_path, "Pipe")
        self.length = 200.0  # 默认值
        self.diameter = 15.0  # 默认值

    def get_parameters(self):
        return {"Length (m)": self.length, "Diameter (cm)": self.diameter}

    def update_parameters_from_inputs(self):
        try:
            self.length = float(self.length_input.text())
            self.diameter = float(self.diameter_input.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(None, "Input Error", "Please enter valid numbers for parameters.")

        
class InletComponent(BaseComponent):
    def __init__(self, icon_path):
        super().__init__(icon_path, "Inlet")
        self.flow_rate = 10.0  # 默认值
        self.pressure = 1.0  # 默认值

    def get_parameters(self):
        return {"Flow Rate (m³/s)": self.flow_rate, "Pressure (bar)": self.pressure}

    def update_parameters_from_inputs(self):
        try:
            self.flow_rate = float(self.flow_rate_input.text())
            self.pressure = float(self.pressure_input.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(None, "Input Error", "Please enter valid numbers for parameters.")


class ValveComponent(BaseComponent):
    def __init__(self, icon_path):
        super().__init__(icon_path, "Valve")
        self.flow_rate = 10.0  # 默认值
        self.pressure = 1.0  # 默认值

class ElbowComponent(BaseComponent):
    def __init__(self, icon_path):
        super().__init__(icon_path, "Elbow")
        self.flow_rate = 10.0  # 默认值
        self.pressure = 1.0  # 默认值

class ReducerComponent(BaseComponent):
    def __init__(self, icon_path):
        super().__init__(icon_path, "Reducer")
        self.flow_rate = 10.0  # 默认值
        self.pressure = 1.0  # 默认值

class OutletComponent(BaseComponent):
    def __init__(self, icon_path):
        super().__init__(icon_path, "Tee")
        self.flow_rate = 10.0  # 默认值
        self.pressure = 1.0  # 默认值

class TeeComponent(BaseComponent):
    def __init__(self, icon_path):
        super().__init__(icon_path, "Outlet")
        self.flow_rate = 10.0  # 默认值
        self.pressure = 1.0  # 默认值