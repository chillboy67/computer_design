# 智能健康管理设计系统

一个基于Python和PyQt5构建的智能健康管理应用，集成了AI大语言模型，为用户提供个性化的健康评估和运动处方服务。

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
- 安全注册/登录
- 凭据自动保存
- 用户历史记录管理

### 🎨 界面特性
- 现代化UI设计
- 流畅的加载动画
- 响应式交互体验

## 技术栈

| 类别 | 技术 |
|------|------|
| GUI框架 | PyQt5 |
| AI集成 | 通义千问/其他LLM API |
| 数据库 | SQLite |
| ORM | SQLAlchemy |

## 目录结构

```
project/
├── main.py             # 程序入口
├── main_window.py       # 主窗口
├── login03.py           # 登录注册界面
├── health_page.py       # 健康评估页面
├── sport_page.py        # 运动处方页面
├── fresh.py              # 加载动画/图像处理
├── ai_for_halthy.py      # AI集成
├── llm_utils.py          # LLM工具类
├── user_service.py       # 用户服务
├── models.py             # 数据模型
├── db_utils.py           # 数据库工具
├── .env                  # 环境配置
└── users.db              # 用户数据库
```

## 快速开始

### 环境要求
- Python 3.8+
- PyQt5
- requests库

### 安装依赖

```bash
pip install PyQt5 requests sqlalchemy
```

### 配置说明

在 `.env` 文件中配置AI服务：

```env
AI_API_KEY=your_api_key
AI_ENDPOINT=your_endpoint
```

### 运行应用

```bash
python main.py
```

## 用户指南

### 登录/注册
1. 首次启动进入登录页面
2. 点击"注册"创建新账户
3. 登录后可选择保存凭据

### 健康评估
1. 登录后进入主界面
2. 点击"健康评估"开始测评
3. AI将根据输入生成健康报告

### 获取运动处方
1. 在健康评估完成后
2. 点击"运动处方"获取个性化建议
3. 可打印或保存报告

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

项目支持多种AI服务集成方式：

```python
from llm_utils import get_LLM_response

# 调用AI获取健康建议
response = get_LLM_response("请分析用户的心血管健康状况...")
```

## 数据库设计

### 用户表
- `id`: 主键
- `username`: 用户名
- `email`: 邮箱
- `password_hash`: 加密密码
- `last_login`: 最后登录时间

### 健康记录表
- `id`: 主键
- `user_id`: 外键关联用户
- `评估数据`: JSON格式存储
- `创建时间`: 记录时间戳

## 安全特性

- 🔒 密码使用哈希加密存储
- 🔑 凭据本地加密保存
- ✅ 管理员账户特殊验证

## 开发路线

- [ ] 添加更多健康指标评估
- [ ] 支持数据导出功能
- [ ] 集成可穿戴设备数据
- [ ] 添加多语言支持

## 许可证

本项目采用 MIT 许可证开源。

## 贡献者

欢迎提交Issue和Pull Request共同完善项目！

原项目https://gitee.com/haotian-tang/computer_design
