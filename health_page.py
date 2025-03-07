import tkinter as tk
from tkinter import ttk


class HealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("健康评估系统")
        self.root.geometry("700x600")

        # 创建Notebook分页容器
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 创建基本信息输入界面
        self.create_basic_info_frame()
        # 创建临床数据输入界面
        self.create_clinical_info_frame()

        # 创建评估结果显示区域
        self.create_results_area()

    def create_basic_info_frame(self):
        """创建基本信息输入界面"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="基本信息")

        # 性别选择
        ttk.Label(frame, text="性别:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.gender = tk.StringVar()
        ttk.Radiobutton(frame, text="男", variable=self.gender, value="男").grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(frame, text="女", variable=self.gender, value="女").grid(row=0, column=2, sticky='w')

        # 年龄输入
        ttk.Label(frame, text="年龄:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.age = ttk.Entry(frame)
        self.age.grid(row=1, column=1, columnspan=2, sticky='we')

        # 身高输入
        ttk.Label(frame, text="身高(cm):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.height = ttk.Entry(frame)
        self.height.grid(row=2, column=1, columnspan=2, sticky='we')

        # 体重输入
        ttk.Label(frame, text="体重(kg):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.weight = ttk.Entry(frame)
        self.weight.grid(row=3, column=1, columnspan=2, sticky='we')

        # 统一设置输入框样式
        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)
        frame.columnconfigure(1, weight=1)

    def create_clinical_info_frame(self):
        """创建临床数据输入界面"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="临床数据")

        # 体成分数据
        ttk.Label(frame, text="体脂率(%):").grid(row=0, column=0, sticky='e')
        self.body_fat = ttk.Entry(frame)
        self.body_fat.grid(row=0, column=1, sticky='we')

        ttk.Label(frame, text="肌肉量(kg):").grid(row=1, column=0, sticky='e')
        self.muscle = ttk.Entry(frame)
        self.muscle.grid(row=1, column=1, sticky='we')

        # 腰围/腰臀比
        ttk.Label(frame, text="腰围(cm):").grid(row=2, column=0, sticky='e')
        self.waist = ttk.Entry(frame)
        self.waist.grid(row=2, column=1, sticky='we')

        ttk.Label(frame, text="腰臀比:").grid(row=3, column=0, sticky='e')
        self.wh_ratio = ttk.Entry(frame)
        self.wh_ratio.grid(row=3, column=1, sticky='we')

        # 代谢指标
        ttk.Label(frame, text="血糖(mmol/L):").grid(row=4, column=0, sticky='e')
        self.glucose = ttk.Entry(frame)
        self.glucose.grid(row=4, column=1, sticky='we')

        ttk.Label(frame, text="血脂(mmol/L):").grid(row=5, column=0, sticky='e')
        self.lipid = ttk.Entry(frame)
        self.lipid.grid(row=5, column=1, sticky='we')

        # 心血管指标
        ttk.Label(frame, text="血压(mmHg):").grid(row=6, column=0, sticky='e')
        self.sbp = ttk.Entry(frame, width=5)
        self.sbp.grid(row=6, column=1, sticky='w')
        ttk.Label(frame, text="/").grid(row=6, column=2)
        self.dbp = ttk.Entry(frame, width=5)
        self.dbp.grid(row=6, column=3, sticky='w')

        ttk.Label(frame, text="心率(bpm):").grid(row=7, column=0, sticky='e')
        self.hr = ttk.Entry(frame)
        self.hr.grid(row=7, column=1, sticky='we')

        # 统一设置输入框样式
        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)
        frame.columnconfigure(1, weight=1)

    def create_results_area(self):
        """创建结果显示区域"""
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="开始评估", command=self.assess_health).pack(side=tk.LEFT, padx=5)

        self.results = tk.Text(self.root, wrap=tk.WORD, height=15, font=('微软雅黑', 10))
        self.results.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def get_float(self, entry):
        """安全获取数值输入"""
        try:
            return float(entry.get())
        except:
            return None

    def assess_health(self):
        """执行健康评估"""
        data = {
            'gender': self.gender.get(),
            'age': self.get_float(self.age),
            'height': self.get_float(self.height),
            'weight': self.get_float(self.weight),
            'body_fat': self.get_float(self.body_fat),
            'muscle': self.get_float(self.muscle),
            'waist': self.get_float(self.waist),
            'wh_ratio': self.get_float(self.wh_ratio),
            'glucose': self.get_float(self.glucose),
            'lipid': self.get_float(self.lipid),
            'sbp': self.get_float(self.sbp),
            'dbp': self.get_float(self.dbp),
            'hr': self.get_float(self.hr)
        }

        report = []
        report.append(self.assess_cardio(data))
        report.append(self.assess_metabolism(data))
        report.append(self.assess_body_comp(data))

        self.show_report([r for r in report if r])

    def show_report(self, reports):
        """显示评估报告"""
        self.results.delete(1.0, tk.END)
        if not reports:
            self.results.insert(tk.END, "⚠️ 请至少填写一项数据以获取评估结果")
            return

        for i, report in enumerate(reports, 1):
            self.results.insert(tk.END, f"{i}. {report['title']}\n")
            self.results.insert(tk.END, "\n".join(f"   • {line}" for line in report['content']))
            self.results.insert(tk.END, "\n\n")

    def assess_cardio(self, data):
        """心血管评估"""
        content = []
        if data['sbp'] and data['dbp']:
            if data['sbp'] >= 140 or data['dbp'] >= 90:
                content.append(f"血压偏高 ({data['sbp']}/{data['dbp']} mmHg)")
            elif data['sbp'] < 90 or data['dbp'] < 60:
                content.append(f"血压偏低 ({data['sbp']}/{data['dbp']} mmHg)")
            else:
                content.append(f"血压正常 ({data['sbp']}/{data['dbp']} mmHg)")

        if data['hr']:
            if data['hr'] > 100:
                content.append(f"心动过速 ({data['hr']} bpm)")
            elif data['hr'] < 60:
                content.append(f"心动过缓 ({data['hr']} bpm)")
            else:
                content.append(f"心率正常 ({data['hr']} bpm)")

        return {'title': '心血管健康评估', 'content': content} if content else None

    def assess_metabolism(self, data):
        """代谢评估"""
        content = []
        if data['glucose']:
            if data['glucose'] >= 7.0:
                content.append(f"空腹血糖偏高 ({data['glucose']} mmol/L)")
            elif data['glucose'] < 3.9:
                content.append(f"空腹血糖偏低 ({data['glucose']} mmol/L)")
            else:
                content.append(f"空腹血糖正常 ({data['glucose']} mmol/L)")

        if data['lipid']:
            if data['lipid'] >= 5.7:
                content.append(f"总胆固醇偏高 ({data['lipid']} mmol/L)")
            else:
                content.append(f"总胆固醇正常 ({data['lipid']} mmol/L)")

        return {'title': '糖脂代谢评估', 'content': content} if content else None

    def assess_body_comp(self, data):
        """体成分评估"""
        content = []

        # BMI计算
        if data['height'] and data['weight']:
            bmi = data['weight'] / ((data['height'] / 100) ** 2)
            status = "肥胖" if bmi >= 28 else "超重" if bmi >= 24 else "正常" if bmi >= 18.5 else "偏瘦"
            content.append(f"BMI指数 {bmi:.1f} ({status})")

        # 体脂率评估
        if data['body_fat'] and data['gender']:
            ranges = {'男': (15, 25), '女': (20, 30)}
            lower, upper = ranges[data['gender']]
            if data['body_fat'] > upper:
                content.append(f"体脂率偏高 ({data['body_fat']}%)")
            elif data['body_fat'] < lower:
                content.append(f"体脂率偏低 ({data['body_fat']}%)")
            else:
                content.append(f"体脂率正常 ({data['body_fat']}%)")

        # 腰围评估
        if data['waist'] and data['gender']:
            threshold = 90 if data['gender'] == '男' else 85
            if data['waist'] >= threshold:
                content.append(f"腰围超标 ({data['waist']}cm)")
            else:
                content.append(f"腰围正常 ({data['waist']}cm)")

        return {'title': '身体成分评估', 'content': content} if content else None


if __name__ == "__main__":
    root = tk.Tk()
    app = HealthApp(root)
    root.mainloop()

