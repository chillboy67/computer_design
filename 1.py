import tkinter as tk
from tkinter import ttk


class HealthApp:
    def __init__(self):
        self.data = {
            "basic": {"gender": "", "age": 0, "height": 0.0, "weight": 0.0},
            "clinical": {"body_fat": 0.0, "muscle_mass": 0.0, "waist": 0.0,
                         "glucose": 0.0, "lipid": 0.0, "bp": "", "heart_rate": 0}
        }

        # 主窗口设置
        self.root = tk.Tk()
        self.root.title("健康评估系统 v1.0")
        self.root.geometry("600x400")

        # 创建多页界面
        self.notebook = ttk.Notebook(self.root)

        # 基本信息页
        self.basic_frame = ttk.Frame(self.notebook)
        self._create_basic_ui()

        # 临床数据页
        self.clinical_frame = ttk.Frame(self.notebook)
        self._create_clinical_ui()

        self.notebook.add(self.basic_frame, text="基本信息")
        self.notebook.add(self.clinical_frame, text="临床数据")
        self.notebook.pack(expand=1, fill="both")

        # 评估按钮
        self.assess_btn = ttk.Button(self.root, text="生成健康评估", command=self.assess_health)
        self.assess_btn.pack(pady=10)

    def _create_basic_ui(self):
        """创建基本信息界面"""
        fields = [
            ("性别", "gender", ["男", "女"]),
            ("年龄", "age", None),
            ("身高(cm)", "height", None),
            ("体重(kg)", "weight", None)
        ]

        for i, (label, key, options) in enumerate(fields):
            ttk.Label(self.basic_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            if options:
                entry = ttk.Combobox(self.basic_frame, values=options, width=18)
            else:
                entry = ttk.Entry(self.basic_frame, width=20)
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, f"basic_{key}", entry)

    def _create_clinical_ui(self):
        """创建临床数据界面"""
        fields = [
            ("体脂率(%)", "body_fat"),
            ("肌肉量(kg)", "muscle_mass"),
            ("腰围(cm)", "waist"),
            ("空腹血糖(mmol/L)", "glucose"),
            ("总血脂(mmol/L)", "lipid"),
            ("血压(如120/80)", "bp"),
            ("静息心率(bpm)", "heart_rate")
        ]

        for i, (label, key) in enumerate(fields):
            ttk.Label(self.clinical_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(self.clinical_frame, width=20)
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, f"clinical_{key}", entry)

    def _get_data(self):
        """收集所有填写的数据"""
        # 收集基本信息
        for key in self.data["basic"]:
            entry = getattr(self, f"basic_{key}")
            value = entry.get()
            if value.replace(".", "").isdigit():
                self.data["basic"][key] = float(value) if "." in value else int(value)
            else:
                self.data["basic"][key] = value

        # 收集临床数据
        for key in self.data["clinical"]:
            entry = getattr(self, f"clinical_{key}")
            value = entry.get()
            if value:
                if key == "bp":
                    self.data["clinical"][key] = value
                else:
                    self.data["clinical"][key] = float(value) if "." in value else int(value)

    def assess_health(self):
        """执行健康评估"""
        self._get_data()
        report = []

        # 心血管评估
        if self.data["clinical"]["bp"] or self.data["clinical"]["heart_rate"]:
            systolic = 0
            if "/" in self.data["clinical"]["bp"]:
                systolic, diastolic = map(int, self.data["clinical"]["bp"].split("/"))

            conditions = []
            if systolic > 140:
                conditions.append("高血压")
            if self.data["clinical"]["heart_rate"] > 100:
                conditions.append("心动过速")
            elif self.data["clinical"]["heart_rate"] < 60:
                conditions.append("心动过缓")

            report.append("心血管评估：" + ("正常" if not conditions else "注意：" + "、".join(conditions)))

        # 糖脂代谢评估
        if self.data["clinical"]["glucose"] or self.data["clinical"]["lipid"]:
            conditions = []
            if self.data["clinical"]["glucose"] > 6.1:
                conditions.append("空腹血糖偏高")
            if self.data["clinical"]["lipid"] > 5.7:
                conditions.append("血脂异常")
            report.append("糖脂代谢评估：" + ("正常" if not conditions else "注意：" + "、".join(conditions)))

        # 体成分评估
        if self.data["basic"]["height"] and self.data["basic"]["weight"]:
            bmi = self.data["basic"]["weight"] / (self.data["basic"]["height"] / 100) ** 2
            status = "肥胖" if bmi >= 28 else "超重" if bmi >= 24 else "正常"
            report.append(f"BMI指数：{bmi:.1f} ({status})")

        if self.data["clinical"]["body_fat"]:
            status = "过高" if (self.data["basic"]["gender"] == "男" and self.data["clinical"]["body_fat"] > 18) or \
                               (self.data["basic"]["gender"] == "女" and self.data["clinical"][
                                   "body_fat"] > 28) else "正常"
            report.append(f"体脂率：{self.data['clinical']['body_fat']}% ({status})")

        # 显示评估结果
        result_window = tk.Toplevel()
        result_window.title("健康评估报告")
        tk.Label(result_window, text="\n".join(report) if report else "请至少填写一项数据").pack(padx=20, pady=20)


if __name__ == "__main__":
    app = HealthApp()
    app.root.mainloop()
