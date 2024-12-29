from PyQt5 import QtWidgets, QtCore, QtGui

class BaseComponent(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, icon_path, component_type):
        super().__init__()
        # 设置组件的图标
        self.setPixmap(QtGui.QPixmap(icon_path).scaled(40, 40, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        self.setFlags(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        # 基础属性
        self.component_type = component_type

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