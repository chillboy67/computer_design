# PyInstaller 打包配置，在项目根目录执行：pyinstaller health_app.spec
# 生成 dist/HealthApp/ 目录，其中的 HealthApp.exe 即为程序入口（Windows 上打包得到 .exe）
from PyInstaller.utils.hooks import collect_data_files

datas = [("assets", "assets")]
datas += collect_data_files("qt_material")  # 主题文件

a = Analysis(
    ["main.py"],
    datas=datas,
    hiddenimports=["PySide6.QtSvg"],  # qt_material 的图标是 SVG
    excludes=["tkinter", "pytest"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="HealthApp",
    console=False,
    icon="assets/app.ico",
)
coll = COLLECT(exe, a.binaries, a.datas, name="HealthApp")
