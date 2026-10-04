# 智能健康管理设计系统
[English](README.md) | 中文

一个基于 Python 和 PySide6（Qt 6）构建的智能健康管理应用，集成了AI大语言模型，为用户提供个性化的健康评估和运动处方服务。

## 功能特点

### 🏥 健康评估
- 心血管健康评估
- 代谢健康分析
- 身体成分分析
- AI驱动的健康报告生成

### 🏃 运动处方
- 个性化运动建议
- 针对性训练计划
- 科学健身指导

### 📈 历史记录与趋势
- 每次生成的报告连同当时填写的数据一起保存
- 可查看、删除历史报告，一键载入上次填写的数据
- 体重、BMI、血压、心率、血糖等指标的变化趋势图，并标注参考线

### 🔐 用户系统
- 注册/登录及输入校验
- “记住密码”使用随机登录令牌实现，不保存明文密码
- 密码使用 bcrypt 哈希存储

### 🎨 界面特性
- Material 风格界面（qt-material）
- AI 流式输出：报告边生成边显示，可随时停止
- 报告以 Markdown 渲染，支持分节浏览、打印和导出 PDF

## 技术栈

| 类别 | 技术 |
|------|------|
| GUI框架 | PySide6 + qt-material + QtCharts |
| AI集成 | 智谱 AI GLM-4（`zhipuai`），可换成其他兼容 OpenAI 接口的大模型 |
| 数据库 | SQLite |
| ORM | SQLAlchemy 2.x |
| 密码哈希 | bcrypt |
| 配置管理 | python-dotenv |
| 打包 | PyInstaller |
| 持续集成 | GitHub Actions |

## 目录结构

```
project/
├── main.py              # 程序入口
├── config.py            # 配置（路径、数据库、AI 服务），从 .env 读取
├── login03.py           # 登录注册界面
├── main_window.py       # 健康数据输入窗口
├── report_page.py       # 报告页公共部分（导航、流式显示、Markdown 渲染、打印/PDF）
├── health_page.py       # 健康评估报告页
├── sport_page.py        # 运动处方报告页
├── history_page.py      # 历史记录与趋势图
├── fresh.py             # 加载动画 + 后台流式请求线程
├── llm_utils.py         # 大模型调用（智谱 AI）
├── prompts.py           # 输入字段定义、提示词构造、返回内容拆分
├── user_service.py      # 用户服务（注册、登录、记住密码令牌）
├── record_service.py    # 健康记录服务（保存、查询、删除、趋势数据）
├── models.py            # 数据模型
├── db_utils.py          # 数据库初始化
├── base.py              # SQLAlchemy 基类
├── assets/              # 图片资源
├── tests/               # 单元测试与界面测试
├── health_app.spec      # PyInstaller 打包配置
├── .github/workflows/   # 持续集成：自动测试、Windows 打包
├── requirements.txt     # 依赖列表
└── .env.example         # 配置模板
```

## 下载使用（Windows，无需安装 Python）

1. 打开 [Build Windows App](https://github.com/chillboy67/computer_design/actions/workflows/build.yml)，点进最新一次成功（绿色 ✓）的运行，在页面底部 **Artifacts** 中下载 `HealthApp-windows`（需要登录 GitHub 账号）
2. 解压后进入 `HealthApp` 文件夹，把 `.env.example` 复制一份并改名为 `.env`
3. 用记事本打开 `.env`，在 `LLM_API_KEY=` 后面填入你的 API Key（见下方[配置说明](#配置说明)）
4. 双击 `HealthApp.exe` 运行，首次使用先注册账号

说明：
- 程序没有数字签名，首次运行时 Windows 可能提示“已保护你的电脑”，点击“更多信息 → 仍要运行”即可
- 账号和历史记录保存在同一文件夹的 `health_db.sqlite` 中，更换版本时保留这个文件和 `.env` 即可
- 下载文件保留 90 天，过期后在上面的页面点击 **Run workflow** 重新打包

## 从源码运行

### 环境要求
- Python 3.10+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置说明

复制 `.env.example` 为 `.env` 并填写。默认使用智谱 AI，只需填写在 [open.bigmodel.cn](https://open.bigmodel.cn/) 申请的 API Key：

```env
LLM_API_KEY=your_api_key
```

也可以换成其他兼容 OpenAI 接口格式的大模型服务，不需要改代码，同时填写接口地址和模型名称即可：

| 服务 | LLM_BASE_URL | LLM_MODEL |
|------|------|------|
| 智谱 AI（默认） | 留空 | `glm-4-plus` |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |

```env
# 例如使用 DeepSeek
LLM_API_KEY=your_deepseek_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

接口地址和模型名称以各服务商的文档为准。旧版配置中的 `ZHIPUAI_API_KEY` 仍然有效。

可选：填写 `DEFAULT_ADMIN_USERNAME` 和 `DEFAULT_ADMIN_PASSWORD`，首次启动时会自动创建演示账号。

`.env` 已加入 `.gitignore`，不会被提交到仓库。

### 运行应用

```bash
python main.py
```

### 运行测试

```bash
pip install -r requirements-dev.txt
pytest
```

界面测试使用 Qt 的 offscreen 模式运行，不会弹出窗口。

### 打包为可执行程序

```bash
pip install pyinstaller
pyinstaller health_app.spec
```

打包结果在 `dist/HealthApp/` 目录（Windows 上运行其中的 `HealthApp.exe`）。把 `.env` 放在可执行文件旁边即可，数据库也会创建在该目录。

每次推送代码时 GitHub Actions 会自动运行测试。没有 Windows 电脑也能打包：在 [Build Windows App](https://github.com/chillboy67/computer_design/actions/workflows/build.yml) 页面点击 **Run workflow**，完成后下载 `HealthApp-windows` 即可。

## 用户指南

### 登录/注册
1. 首次启动进入登录页面
2. 点击"注册"创建新账户
3. 勾选“记住密码”后，下次启动无需再输入密码

### 健康评估
1. 登录后进入主界面
2. 填写年龄、身高、体重（必填）及已有的临床数据
3. 点击"健康评估"，AI 将生成包含心血管健康、糖脂代谢、体成分三部分的报告

### 获取运动处方
1. 填写同样的健康数据
2. 点击"运动处方"获取运动项目、频率、强度及注意事项
3. 可打印报告或保存为 PDF

### 历史记录与趋势
1. 点击"历史记录与趋势"查看所有历史报告
2. 双击记录可重新打开报告；选择指标可查看其变化趋势
3. 在主界面点击"载入上次数据"可自动填入上次的数据

## 系统架构

```
┌─────────────────┐     ┌──────────────────┐
│   MainWindow    │────▶│  HealthPage      │
│                 │     │  - 心血管评估      │
├─────────────────┤     │  - 代谢分析       │
│  用户认证模块     │────▶│  - 身体分析       │
│  - 登陆          │     └─────────────────┘
│  - 注册          │     
├─────────────────┤     ┌─────────────────┐
│  服务层          │────▶│  SportPage      │
│  - UserService  │     │  - 运动处方      │
│  - DbUtils      │     │  - 训练计划      │
└─────────────────┘     └─────────────────┘

        AI 服务
    ┌─────────────┐
    │  get_LLM_   │
    │  response() │
    └─────────────┘
```

## API集成

调用哪个服务由 `.env` 中的 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 决定：

```python
from llm_utils import get_health_assessment, stream_health_assessment
from prompts import build_health_prompt

data = {"gender": "男", "age": 30, "height": 175, "weight": 70}
report = get_health_assessment(build_health_prompt(data))  # 返回完整 Markdown 文本

for piece in stream_health_assessment(build_health_prompt(data)):  # 流式输出
    print(piece, end="")
```

系统提示词要求模型按固定的 `##` 二级标题输出 Markdown，`prompts.split_sections()` 据此把报告拆分为各个部分。

## 数据库设计

### 用户表（`users`）
- `id`: 主键
- `username`: 用户名（唯一）
- `email`: 邮箱（选填）
- `password_hash`: bcrypt 哈希
- `remember_token_hash`: “记住密码”令牌的 SHA-256
- `created_at` / `last_login`: 创建时间 / 最后登录时间

### 健康记录表（`health_records`）
- `id`: 主键
- `user_id`: 外键关联用户
- `record_type`: `health`（健康评估）或 `sport`（运动处方）
- `gender` / `age` / `height` / `weight` / `bmi` / `body_fat` / `muscle_mass` / `waist`
- `sbp` / `dbp` / `heart_rate` / `glucose` / `triglycerides`
- `report_text`: 生成的报告（Markdown）
- `created_at`: 记录时间

启动时会自动为旧版本数据库补齐缺少的列，旧数据可以继续使用。

## 安全特性

- 🔒 密码使用 bcrypt 哈希存储
- 🔑 “记住密码”在本地只保存随机令牌，数据库只保存令牌哈希，不保存密码
- 🗝️ API Key 等敏感配置从 `.env` 读取，不提交到仓库

## 免责声明

报告由 AI 生成，仅供健康管理参考，不能替代医生的诊断和治疗。

## 开发路线

- [x] 保存历史评估记录并展示指标趋势
- [x] 流式输出
- [x] 打包为 Windows 可执行程序
- [ ] 添加更多健康指标评估
- [ ] 集成可穿戴设备数据
- [ ] 添加多语言支持

## 许可证

本项目采用 MIT 许可证开源。

## 贡献者

欢迎提交Issue和Pull Request共同完善项目！

原项目https://gitee.com/haotian-tang/computer_design
