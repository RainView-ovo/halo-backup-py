# halo-backup-py

> 一键备份 Halo 博客站点到本地的 Python 工具，支持自动下载与远端清理

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green)

## 简介

halo-backup-py 是一个轻量级的 Python 命令行工具，通过调用 [Halo](https://github.com/halo-dev/halo) 博客平台的 [Migration API](https://docs.halo.run/api)，自动完成以下流程：

1. **发起备份** — 向 Halo 服务端请求创建站点全量备份
2. **等待完成** — 轮询备份状态，直到备份成功
3. **自动下载** — 将备份文件流式下载到本地，实时显示进度条
4. **可选清理** — 下载完成后可选择自动删除服务端备份文件

全程日志记录，开箱即用。

## 功能特性

- ✅ **一键全自动** — 从发起备份到下载完成全自动执行
- 📊 **进度可视化** — 使用 `tqdm` 实时显示下载进度和速率
- 🧹 **自动清理** — 支持下载后自动删除远端备份，节省服务端存储
- ⏱ **自定义保留时间** — 可设置备份在服务端的过期时间
- 📝 **日志记录** — 控制台彩色输出 + 文件日志（按日轮转，保留 90 天）
- 🔧 **配置驱动** — 使用 `.env` 管理所有参数，无需修改代码

## 快速开始

### 前置条件

- Python 3.8+
- 一个 Halo 博客站点

### 安装

```bash
# 克隆仓库
git clone https://github.com/RainView-ovo/halo-backup-py.git
cd halo-backup-py

# 安装依赖
pip install -r requirements.txt
```

### 配置

复制 `.env.example` 为 `.env`，填入你的博客信息：

```bash
cp .env.example .env
```

```dotenv
# 备份在 Halo 上的保留时间（秒），259200 = 3 天
RETENTION_TIME=259200

# 要备份的博客地址（带 http/https）
DOMAIN=https://your-blog.com

# 个人令牌，需要前往 Halo 后台创建
# 路径：系统 → 个人令牌 → 新建令牌（需要「备份」相关权限）
PERSONAL_TOKEN=pat_xxxxxxxxxxxxx

# 本地保存位置
SAVE_LOCATION=/path/to/save

# 备份完成后是否自动下载到本地（true/false）
AUTO_DOWN=true

# 下载完成后是否删除 Halo 上的备份（true/false）
DEL_BAK=true
```

### 运行

```bash
python main.py
```

## 文件结构

```
halo-backup-py/
├── main.py          # 主入口：编排备份→等待→下载→清理流程
├── api_halo.py      # API 封装层：备份、状态查询、下载、删除操作
├── .env             # 配置文件（从 .env.example 复制并修改）
├── .env.example     # 配置示例
├── requirements.txt # Python 依赖
└── logs/            # 日志文件（自动生成）
```

## API 说明

工具使用 Halo 的 Migration API，具体端点：

| 操作 | HTTP 方法 | 端点 |
|------|-----------|------|
| 创建备份 | POST | `/apis/migration.halo.run/v1alpha1/backups` |
| 查询状态 | GET | `/apis/migration.halo.run/v1alpha1/backups` |
| 下载备份 | GET | `/apis/console.api.migration.halo.run/v1alpha1/backups/{name}/files/{filename}` |
| 删除备份 | DELETE | `/apis/migration.halo.run/v1alpha1/backups/{name}` |

## 日志

- 控制台输出格式：`[2026-06-02 14:30:00] [INFO] 请求发起备份……`
- 文件日志保存在 `logs/` 目录，按日滚动，保留 90 天

## 常见问题

**Q: 如何获取 `personal_token`？**
A: 登录 Halo 后台 → 系统 → 个人令牌 → 新建令牌，确保勾选备份相关的权限。

## 许可证

[MIT](LICENSE)