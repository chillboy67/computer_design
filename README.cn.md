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

### 🔐 用户系统
- 注册/登录及输入校验
- “记住密码”使用随机登录令牌实现，不保存明文密码
- 密码使用 bcrypt 哈希存储

### 🎨 界面特性
- Material 风格界面（qt-material）
- AI 请求在后台线程执行，加载动画期间可取消
- 报告以 Markdown 渲染，支持分节浏览、打印和导出 PDF

## 技术栈

| 类别 | 技术 |
|------|------|
| GUI框架 | PySide6 + qt-material |
| AI集成 | 智谱 AI GLM-4（`zhipuai`） |
| 数据库 | SQLite |
| ORM | SQLAlchemy 2.x |
| 密码哈希 | bcrypt |
| 配置管理 | python-dotenv |

## 目录结构

```
project/
├── main.py              # 程序入口
├── config.py            # 配置（路径、数据库、AI 服务），从 .env 读取
├── login03.py           # 登录注册界面
├── main_window.py       # 健康数据输入窗口
├── report_page.py       # 报告页公共部分（导航、Markdown 渲染、打印/PDF）
├── health_page.py       # 健康评估报告页
├── sport_page.py        # 运动处方报告页
├── fresh.py             # 加载动画 + 后台 AI 请求线程
├── llm_utils.py         # 大模型调用（智谱 AI）
├── prompts.py           # 输入字段定义、提示词构造、返回内容拆分
├── user_service.py      # 用户服务（注册、登录、记住密码令牌）
├── models.py            # 数据模型
├── db_utils.py          # 数据库初始化
├── base.py              # SQLAlchemy 基类
├── assets/              # 图片资源
├── tests/               # 单元测试
├── requirements.txt     # 依赖列表
└── .env.example         # 配置模板
```

## 快速开始

### 环境要求
- Python 3.9+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置说明

复制 `.env.example` 为 `.env`，并填写智谱 AI 的 API Key（[open.bigmodel.cn](https://open.bigmodel.cn/)）：

```env
ZHIPUAI_API_KEY=your_api_key
LLM_MODEL=glm-4-plus
# 可选：首次启动时创建演示账号
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=your_demo_password
```

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

```python
from llm_utils import get_health_assessment, get_sport_prescription
from prompts import build_health_prompt

data = {"gender": "男", "age": 30, "height": 175, "weight": 70}
report = get_health_assessment(build_health_prompt(data))  # 返回 Markdown 文本
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
- `sbp` / `dbp` / `glucose` / `triglycerides`: 关键指标
- `created_at`: 记录时间

启动时会自动为旧版本数据库补齐缺少的列，旧数据可以继续使用。

## 安全特性

- 🔒 密码使用 bcrypt 哈希存储
- 🔑 “记住密码”在本地只保存随机令牌，数据库只保存令牌哈希，不保存密码
- 🗝️ API Key 等敏感配置从 `.env` 读取，不提交到仓库

## 免责声明

报告由 AI 生成，仅供健康管理参考，不能替代医生的诊断和治疗。

## 开发路线

- [ ] 保存历史评估记录并展示指标趋势
- [ ] 添加更多健康指标评估
- [ ] 集成可穿戴设备数据
- [ ] 添加多语言支持

## 许可证

本项目采用 MIT 许可证开源。

## 贡献者

欢迎提交Issue和Pull Request共同完善项目！

原项目https://gitee.com/haotian-tang/computer_design
