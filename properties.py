class Properties:
    def __init__(self):
        self.nc = 0  # 组分数，int
        self.ft = ["kmol/h", 0.0]  # 总摩尔流量，列表形式 [单位, 数值]
        self.comps = []  # 组分列表，字符串形式
        self.fs = []  # 组分流量分布，列表形式 [组分种类, 单位, 摩尔百分比]
        self.method = None  # 物性方法，int
        self.calc_type = "PT"  # 计算类型，字符串形式，默认 "PT"
        self.variable1 = ["", 0.0]  # 变量1
        self.variable2 = ["", 0.0]  # 变量2

    def update_nc(self, nc):
        self.nc = nc

    def update_ft(self, unit, value):
        self.ft = [unit, float(value)]

    def update_comps(self, comps):
        self.comps = comps
        
    def update_fs(self, fs):
        self.fs = fs  

    def update_method(self, method):
        self.method = method

    def update_calc_type(self, calc_type):
        self.calc_type = calc_type

    def update_variable1(self, unit, value):
        self.variable1 = [unit, float(value)]

    def update_variable2(self, unit, value):
        self.variable2 = [unit, float(value)]

    def reset(self):
        self.__init__()

    def as_dict(self):
        return {
            "nc": self.nc,
            "ft": self.ft,
            "comps": self.comps,
            "fs": self.fs,
            "method": self.method,
            "calc_type": self.calc_type,
            "variable1": self.variable1,
            "variable2": self.variable2,
        }

    def update_from_dict(self, data):
        self.nc = data.get("nc", self.nc)
        self.update_ft(*data.get("ft", self.ft))
        self.update_comps(data.get("comps", self.comps))
        self.update_fs(data.get("fs", self.fs))
        self.update_method(data.get("method", self.method))
        self.update_calc_type(data.get("calc_type", self.calc_type))
        self.update_variable1(*data.get("variable1", self.variable1))
        self.update_variable2(*data.get("variable2", self.variable2))

    def __str__(self):
        return (f"Properties(nc={self.nc}, ft={self.ft}, comps={self.comps}, fs={self.fs}, "
                f"method={self.method}, calc_type={self.calc_type}, variable1={self.variable1}, variable2={self.variable2})")

# 创建一个 Properties 实例
props = Properties()

new_data = {
    "nc": 2,
    "ft": ["kmol/h", 150.0],
    "comps": ["CO2", "H2O"],
    "fs": [["CO2", "kmol", 80.0], ["H2O", "kmol", 20.0]],
    "method": 19,
    "calc_type": "PT",
    "variable1": ["bara", 10],
    "variable2": ["C", 25.0]
}
props.update_from_dict(new_data)
print(props)