from PyQt5 import QtWidgets, QtCore, QtGui
from properties import *
from Gasflow_Equation import *
import copy

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
        # 显示标题和按钮
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(f"{self.component_type} Parameters")

        # 动态生成输入字段
        layout = QtWidgets.QFormLayout(dialog)

        # 添加按钮
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec_()

    def contextMenuEvent(self, event):
        # 添加右键菜单，用于查看出口物性参数
        menu = QtWidgets.QMenu()
        show_results_action = menu.addAction("Show Outlet Properties")
        action = menu.exec_(event.screenPos())

        if action == show_results_action:
            self.show_outlet_properties_dialog()

    def show_outlet_properties_dialog(self):
        # 显示出口物性参数的对话框
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(f"{self.component_type} Outlet Properties")

        layout = QtWidgets.QFormLayout(dialog)

        if hasattr(self, "outlet_properties") and self.outlet_properties:
            properties = self.outlet_properties.as_dict()
            for key, value in properties.items():
                layout.addRow(QtWidgets.QLabel(f"{key.capitalize()}: {value}"))
        else:
            layout.addRow(QtWidgets.QLabel("No outlet properties available."))

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec_()

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
                connection.update_connectionline()
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



class InletComponent(BaseComponent):
    def __init__(self, icon_path):
        super().__init__(icon_path, "Inlet")
        # 初始化入口物性参数
        self.nc = 0  # 组分数，int
        self.ft = ["kmol", 10.0]  # 总摩尔流量，列表形式 [单位, 数值]
        self.comps = []  # 组分列表，字符串形式
        self.fs = []  # 组分流量分布，列表形式 [组分种类, 单位, 摩尔百分比]
        self.method = 19  # 物性方法，int
        self.calc_type = "PT"  # 计算类型，字符串形式，默认 "PT"
        self.variable1 = ["bara", 10.0]  # 变量1
        self.variable2 = ["C", 10.0]  # 变量2

        # 初始化出口物性参数
        self.inlet_properties = Properties()
        self.outlet_properties = Properties()


    def add_connection_points(self):
            """
            仅添加右连接点
            """
            self.right_point = QtWidgets.QGraphicsEllipseItem(self.pixmap().width(), self.pixmap().height() / 2 - 5, 10, 10, self)
            self.right_point.setBrush(QtGui.QBrush(QtCore.Qt.red))
            self.right_point.setPen(QtGui.QPen(QtCore.Qt.red, 2))
            self.right_point.setZValue(self.zValue() + 1)
            self.right_point.setData(QtCore.Qt.UserRole, "right_point")  # 添加标识


    def show_input_dialog(self):
        """
        显示入口物性参数的输入窗口
        """
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(f"{self.component_type} Parameters")

        layout = QtWidgets.QFormLayout(dialog)

        # 输入组分数
        nc_input = QtWidgets.QSpinBox()
        nc_input.setRange(1, 100)  # 设置合理范围
        nc_input.setValue(self.nc)
        layout.addRow("Number of Components (nc):", nc_input)

        # 总摩尔流量
        ft_unit_input = QtWidgets.QLineEdit(self.ft[0])
        ft_value_input = QtWidgets.QLineEdit(str(self.ft[1]))
        ft_layout = QtWidgets.QHBoxLayout()
        ft_layout.addWidget(ft_value_input)
        ft_layout.addWidget(ft_unit_input)
        layout.addRow("Total Molar Flow (ft):", ft_layout)

        # 组分名称
        comps_layout = QtWidgets.QFormLayout()
        fs_layout = QtWidgets.QFormLayout()
        comps_inputs = []
        fs_inputs = []

        def update_comps_and_fs():
            """
            动态更新 comps 和 fs 的输入框
            """
            # 清空现有的行
            for i in reversed(range(comps_layout.rowCount())):
                comps_layout.removeRow(i)
            for i in reversed(range(fs_layout.rowCount())):
                fs_layout.removeRow(i)

            comps_inputs.clear()
            fs_inputs.clear()

            for i in range(nc_input.value()):
                # 组分名称
                comp_input = QtWidgets.QLineEdit(self.comps[i] if i < len(self.comps) else "")
                comps_layout.addRow(f"Component {i + 1}:", comp_input)
                comps_inputs.append(comp_input)

                # 流量分布中的单位和数值输入框
                fs_species_label = QtWidgets.QLabel(comp_input.text())
                fs_unit_input = QtWidgets.QLineEdit(self.fs[i][1] if i < len(self.fs) else "kmol")
                fs_value_input = QtWidgets.QLineEdit(str(self.fs[i][2]) if i < len(self.fs) else "0.0")
                fs_row_layout = QtWidgets.QHBoxLayout()
                fs_row_layout.addWidget(fs_species_label)
                fs_row_layout.addWidget(fs_unit_input)
                fs_row_layout.addWidget(fs_value_input)
                fs_inputs.append((fs_species_label, fs_unit_input, fs_value_input))
                fs_layout.addRow(f"Flow Distribution {i + 1}:", fs_row_layout)

                # 动态同步组分名称
                def sync_species_name(comp_input, fs_species_label):
                    def inner():
                        fs_species_label.setText(comp_input.text())
                    return inner

                comp_input.textChanged.connect(sync_species_name(comp_input, fs_species_label))

        # 动态更新 comps 和 fs 输入框
        nc_input.valueChanged.connect(update_comps_and_fs)
        update_comps_and_fs()

        layout.addRow("Components:", comps_layout)
        layout.addRow("Flow Distributions:", fs_layout)

        # 输入其他参数
        method_input = QtWidgets.QLineEdit(str(self.method) if self.method is not None else "")
        calc_type_input = QtWidgets.QLineEdit(self.calc_type)
        layout.addRow("Property Method:", method_input)
        layout.addRow("Calculation Type:", calc_type_input)

        # 输入变量1和变量2
        var1_unit_input = QtWidgets.QLineEdit(self.variable1[0])
        var1_value_input = QtWidgets.QLineEdit(str(self.variable1[1]))
        var1_layout = QtWidgets.QHBoxLayout()
        var1_layout.addWidget(var1_value_input)
        var1_layout.addWidget(var1_unit_input)
        layout.addRow("Variable 1:", var1_layout)

        var2_unit_input = QtWidgets.QLineEdit(self.variable2[0])
        var2_value_input = QtWidgets.QLineEdit(str(self.variable2[1]))
        var2_layout = QtWidgets.QHBoxLayout()
        var2_layout.addWidget(var2_value_input)
        var2_layout.addWidget(var2_unit_input)
        layout.addRow("Variable 2:", var2_layout)

        # 确认和取消按钮
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # 显示对话框并获取输入
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            self.nc = nc_input.value()
            self.ft = [ft_unit_input.text(), float(ft_value_input.text())]
            self.comps = [comp_input.text() for comp_input in comps_inputs]
            self.fs = [
                [
                    fs_input[0].text(),  # 同步的组分名称
                    fs_input[1].text(),  # 单位
                    float(fs_input[2].text()),  # 数值
                ]
                for fs_input in fs_inputs
                if len(fs_input) == 3  # 确保 fs_input 包含三个元素
            ]
            self.method = int(method_input.text()) if method_input.text().isdigit() else None
            self.calc_type = calc_type_input.text()
            self.variable1 = [var1_unit_input.text(), float(var1_value_input.text())]
            self.variable2 = [var2_unit_input.text(), float(var2_value_input.text())]

            # 更新出口物性参数
            self.outlet_properties.update_from_dict(
                {
                    "nc": self.nc,
                    "ft": self.ft,
                    "comps": self.comps,
                    "fs": self.fs,
                    "method": self.method,
                    "calc_type": self.calc_type,
                    "variable1": self.variable1,
                    "variable2": self.variable2,
                }
            )
            print(self.outlet_properties)


class PipeComponent(BaseComponent):
    def __init__(self, icon_path):
        super().__init__(icon_path, "Pipe")
        self.diameter = ["m", 0.2027174]
        self.roughness = ["m", 0.000046]
        self.length = ["m", 800]
        self.elevation = ["m", 0]
        self.section_number = 10
        self.heat_loss = ["j/kg/m", 0]

        # 物性参数
        self.inlet_properties = None  # 入口物性参数
        self.outlet_properties = None  # 出口物性参数

    def show_input_dialog(self):
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(f"{self.component_type} Parameters")

        layout = QtWidgets.QFormLayout(dialog)

        # 动态生成输入字段
        self.diameter_unit_input = QtWidgets.QLineEdit(self.diameter[0])
        self.diameter_value_input = QtWidgets.QLineEdit(str(self.diameter[1]))
        diameter_layout = QtWidgets.QHBoxLayout()
        diameter_layout.addWidget(self.diameter_value_input)
        diameter_layout.addWidget(self.diameter_unit_input)
        layout.addRow("Diameter:", diameter_layout)

        self.roughness_unit_input = QtWidgets.QLineEdit(self.roughness[0])
        self.roughness_value_input = QtWidgets.QLineEdit(str(self.roughness[1]))
        roughness_layout = QtWidgets.QHBoxLayout()
        roughness_layout.addWidget(self.roughness_value_input)
        roughness_layout.addWidget(self.roughness_unit_input)
        layout.addRow("Roughness:", roughness_layout)

        self.length_unit_input = QtWidgets.QLineEdit(self.length[0])
        self.length_value_input = QtWidgets.QLineEdit(str(self.length[1]))
        length_layout = QtWidgets.QHBoxLayout()
        length_layout.addWidget(self.length_value_input)
        length_layout.addWidget(self.length_unit_input)
        layout.addRow("Length:", length_layout)

        # elevation 输入字段
        self.elevation_unit_input = QtWidgets.QLineEdit(self.elevation[0])
        self.elevation_value_input = QtWidgets.QLineEdit(str(self.elevation[1]))
        elevation_layout = QtWidgets.QHBoxLayout()
        elevation_layout.addWidget(self.elevation_value_input)
        elevation_layout.addWidget(self.elevation_unit_input)
        layout.addRow("Elevation:", elevation_layout)

        self.section_number_input = QtWidgets.QLineEdit(str(self.section_number))
        layout.addRow("Section Number:", self.section_number_input)

        self.heat_loss_unit_input = QtWidgets.QLineEdit(self.heat_loss[0])
        self.heat_loss_value_input = QtWidgets.QLineEdit(str(self.heat_loss[1]))
        heat_loss_layout = QtWidgets.QHBoxLayout()
        heat_loss_layout.addWidget(self.heat_loss_value_input)
        heat_loss_layout.addWidget(self.heat_loss_unit_input)
        layout.addRow("Heat Loss:", heat_loss_layout)

        # 添加按钮
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            try:
                # 更新输入参数
                self.diameter = [self.diameter_unit_input.text(), float(self.diameter_value_input.text())]
                self.roughness = [self.roughness_unit_input.text(), float(self.roughness_value_input.text())]
                self.length = [self.length_unit_input.text(), float(self.length_value_input.text())]
                self.elevation = [self.elevation_unit_input.text(), float(self.elevation_value_input.text())]
                self.section_number = int(self.section_number_input.text())
                self.heat_loss = [self.heat_loss_unit_input.text(), float(self.heat_loss_value_input.text())]
            except ValueError:
                QtWidgets.QMessageBox.warning(None, "Input Error", "Please enter valid numbers for parameters.")

    def fake_pipe_pressure_drop(self, properties):

        # 创建一个新的 Properties 对象，复制原始值
        new_properties = Properties()
        new_properties.update_nc(properties.nc)
        new_properties.update_ft(*properties.ft)
        new_properties.update_comps(properties.comps)
        new_properties.update_fs(properties.fs)
        new_properties.update_method(properties.method)
        new_properties.update_calc_type(properties.calc_type)


        new_variable1, new_variable2 = outlet_condition(properties.nc, properties.ft, properties.comps, properties.fs,
                                                        properties.variable1, properties.variable2, properties.method,
                                                        self.roughness[1], self.diameter[1], self.length[1], self.elevation[1], self.section_number, self.heat_loss[1])
        new_properties.update_variable1(new_variable1[0], new_variable1[1])
        new_properties.update_variable2(new_variable2[0], new_variable2[1])

        return new_properties

    def update_inlet_properties(self, inlet_properties):
        # 从上游组件接收入口物性参数
        self.inlet_properties = inlet_properties

    def calculate_outlet_properties(self):
        try:
            self.outlet_properties = self.fake_pipe_pressure_drop(copy.deepcopy(self.inlet_properties))
            print(f"{self.component_type} Outlet Properties: {self.outlet_properties}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, "Calculation Error", f"An error occurred during calculation: {e}")
            # 保留程序最后一次正确的参数
            self.outlet_properties = copy.deepcopy(self.inlet_properties)




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