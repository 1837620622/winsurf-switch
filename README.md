# 🚀 Windsurf 账号切换器

**突破 Claude 4.5 模型 30 分钟等待限制的终极解决方案！**

通过多账号轮询切换，实现 Claude 4.5 无限制使用。支持 **Windows** 和 **macOS** 双平台。

> ⭐ **如果觉得有用，请给个 Star 支持一下！**

---

## 🔗 关联项目

| 项目 | 说明 | 链接 |
|------|------|------|
| **Windsurf-Switcher-Free** | VS Code/Windsurf 插件版本，无需单独运行程序 | [GitHub](https://github.com/1837620622/Windsurf-Switcher-Free) |

> 💡 **推荐**：如果你更喜欢在 Windsurf 内直接切换账号，可以使用插件版本！

---

## � 下载安装

### 方式一：直接下载可执行文件（推荐）

前往 [Releases 页面](https://github.com/1837620622/winsurf-switch/releases) 下载：

| 系统 | 下载文件 |
|------|---------|
| Windows | `Windsurf账号切换器_Windows.exe` |
| macOS | `Windsurf账号切换器_Mac.dmg` |

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/1837620622/winsurf-switch.git
cd winsurf-switch

# macOS 运行
python3 windsurf_mac.py

# Windows 运行
python windsurf_win.py
```

---

## ✨ 功能特性

- 🔄 **多账号快速切换** - 一键切换已保存的 Windsurf 账号
- 💾 **账号配置备份** - 完整备份登录状态，无需重复登录
- 🖥️ **双平台支持** - Windows 和 macOS 原生适配
- 🎯 **图形化界面** - 简洁直观的 GUI 操作
- 🔒 **本地存储** - 账号数据保存在本地，安全可靠

---

## 📋 使用场景

当使用 Windsurf 的 Claude 4.5 模型时，官方限制每 30 分钟只能发送一定数量的请求。通过本工具，你可以：

1. 注册多个 Windsurf 账号
2. 将每个账号的登录状态备份到本工具
3. 当一个账号达到限制时，切换到另一个账号继续使用
4. 实现 **Claude 4.5 无等待轮询使用**

---

## 🛠️ 安装与使用

### 环境要求

- **Python 3.6+**（Windows 和 macOS 均需安装）
- **Tkinter**（Python 自带，无需额外安装）

### macOS 使用步骤

#### 第一步：备份账号

1. 在 Windsurf 中 **手动登录** 第一个账号
2. **完全关闭 Windsurf**（确保进程已退出）
3. 运行账号切换器：
   ```bash
   python3 windsurf_mac.py
   ```
4. 点击 **「保存当前账号」** 按钮
5. 输入配置名称（建议使用邮箱前缀便于识别）
6. 重复以上步骤，备份所有账号

#### 第二步：切换账号

1. **完全关闭 Windsurf**
2. 运行账号切换器
3. 在列表中选择目标账号
4. 点击 **「切换账号」** 按钮
5. 等待提示切换成功
6. 重新启动 Windsurf 即可使用新账号

### Windows 使用步骤

#### 第一步：备份账号

1. 在 Windsurf 中 **手动登录** 第一个账号
2. **完全关闭 Windsurf**（检查任务管理器确保进程已退出）
3. 运行账号切换器：
   ```cmd
   python windsurf_win.py
   ```
4. 点击 **「保存当前账号」** 按钮
5. 输入配置名称（建议使用邮箱前缀便于识别）
6. 重复以上步骤，备份所有账号

#### 第二步：切换账号

1. **完全关闭 Windsurf**（确保任务管理器中无 Windsurf.exe 进程）
2. 运行账号切换器
3. 在列表中选择目标账号
4. 点击 **「切换账号」** 按钮
5. 等待提示切换成功
6. 重新启动 Windsurf 即可使用新账号

---

## ⚠️ 重要注意事项

### 必须手动登录

本工具 **不提供自动登录功能**，你需要：

1. 首先在 Windsurf 中手动完成登录
2. 登录成功后关闭 Windsurf
3. 使用本工具备份已登录的账号状态

### 必须关闭 Windsurf

在执行 **保存** 或 **切换** 操作前，必须完全关闭 Windsurf：

- **macOS**: 使用 `Cmd + Q` 退出，或在程序中点击强制关闭
- **Windows**: 确保任务管理器中没有 `Windsurf.exe` 进程

如果 Windsurf 正在运行，工具会提示是否强制关闭。

### 账号数据安全

- 账号配置保存在 `windsurf_profiles/` 目录中
- 该目录已在 `.gitignore` 中排除，不会被上传到 Git
- 请妥善保管此目录，切勿泄露

---

## 📁 项目结构

```
windsurf-switch/
├── windsurf_mac.py      # macOS 版本主程序
├── windsurf_win.py      # Windows 版本主程序
├── windsurf_profiles/   # 账号配置存储目录（自动创建）
├── README.md            # 说明文档
└── .gitignore           # Git 忽略配置
```

---

## 🔧 技术原理

本工具通过备份和还原以下 Windsurf 数据实现账号切换：

| 数据类型 | macOS 路径 | Windows 路径 |
|---------|-----------|-------------|
| 认证状态 | `~/Library/Application Support/Windsurf/User/globalStorage/` | `%APPDATA%\Windsurf\User\globalStorage\` |
| Session | `~/Library/Application Support/Windsurf/Session Storage/` | `%APPDATA%\Windsurf\Session Storage\` |
| Cookies | `~/Library/Application Support/Windsurf/Cookies` | `%APPDATA%\Windsurf\Network\` |
| Codeium | `~/.codeium/windsurf/` | `%USERPROFILE%\.codeium\windsurf\` |

---

## 🤝 轮询使用建议

为了高效使用 Claude 4.5 模型，建议：

1. **准备 2-3 个账号** - 基本满足连续使用需求
2. **及时切换** - 当提示达到限制时立即切换
3. **合理规划** - 重要任务优先，避免频繁切换
4. **记录状态** - 可在配置名称中标注账号用途

---

## 📞 联系作者

- **微信**: 1837620622（传康kk）
- **邮箱**: 2040168455@qq.com
- **咸鱼 / B站**: 万能程序员

---

## 📄 免责声明

本工具仅供学习和个人使用，请遵守 Windsurf 的服务条款。作者不对任何滥用行为负责。

---

## ⭐ Star 支持

如果这个工具帮助到了你，欢迎给个 Star ⭐ 支持一下！
