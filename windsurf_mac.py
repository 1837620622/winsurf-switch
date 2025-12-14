"""
Windsurf 账号快速切换工具 (Mac版本)
功能：
1. 保存当前账号为Profile
2. 切换到已保存的Profile
3. 列出所有Profile
4. 删除Profile
"""

import os
import sys
import json
import shutil
import sqlite3
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from pathlib import Path

# ============================================================
# Mac 系统路径配置
# ============================================================
HOME = os.path.expanduser('~')

# Windsurf 应用数据目录 (Mac路径)
WINDSURF_DATA = os.path.join(HOME, 'Library', 'Application Support', 'Windsurf')
WINDSURF_USER = os.path.join(WINDSURF_DATA, 'User')
WINDSURF_GLOBAL_STORAGE = os.path.join(WINDSURF_USER, 'globalStorage')
STATE_DB = os.path.join(WINDSURF_GLOBAL_STORAGE, 'state.vscdb')
STORAGE_JSON = os.path.join(WINDSURF_GLOBAL_STORAGE, 'storage.json')

# 需要备份的额外目录
SESSION_STORAGE = os.path.join(WINDSURF_DATA, 'Session Storage')
LOCAL_STORAGE = os.path.join(WINDSURF_DATA, 'Local Storage')

# Mac 特有的认证相关文件 (与 Windows 不同，Mac 没有 Network 目录)
COOKIES_FILE = os.path.join(WINDSURF_DATA, 'Cookies')
COOKIES_JOURNAL = os.path.join(WINDSURF_DATA, 'Cookies-journal')
NETWORK_STATE_FILE = os.path.join(WINDSURF_DATA, 'Network Persistent State')

# Codeium 配置目录 (Mac路径)
CODEIUM_DIR = os.path.join(HOME, '.codeium', 'windsurf')

# Profile存储目录 (保存到脚本运行的当前目录)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_DIR = os.path.join(SCRIPT_DIR, 'windsurf_profiles')


# ============================================================
# Windsurf 账号切换器主类
# ============================================================
class WindsurfAccountSwitcher:
    def __init__(self, root):
        """
        初始化账号切换器
        参数:
            root: tkinter主窗口对象
        """
        self.root = root
        self.root.title("Windsurf 账号切换器 (Mac) - 开源免费")
        self.root.geometry("550x560")
        self.root.resizable(True, True)
        
        # 确保Profile目录存在
        os.makedirs(PROFILES_DIR, exist_ok=True)
        
        # 初始化UI和数据
        self.setup_ui()
        self.refresh_profiles()
        self.show_current_account()
    
    # --------------------------------------------------------
    # UI 界面设置
    # --------------------------------------------------------
    def setup_ui(self):
        """设置用户界面"""
        # 当前账号信息区域
        info_frame = ttk.LabelFrame(self.root, text="当前账号", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Mac系统使用系统默认字体
        self.current_account_label = ttk.Label(info_frame, text="正在读取...", font=('PingFang SC', 12))
        self.current_account_label.pack(anchor=tk.W)
        
        self.current_email_label = ttk.Label(info_frame, text="", foreground='gray')
        self.current_email_label.pack(anchor=tk.W)
        
        # Profile列表区域
        list_frame = ttk.LabelFrame(self.root, text="已保存的账号配置", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Treeview表格
        columns = ('name', 'email', 'date')
        self.profile_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.profile_tree.heading('name', text='配置名称')
        self.profile_tree.heading('email', text='邮箱')
        self.profile_tree.heading('date', text='保存时间')
        self.profile_tree.column('name', width=120)
        self.profile_tree.column('email', width=200)
        self.profile_tree.column('date', width=160)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.profile_tree.yview)
        self.profile_tree.configure(yscrollcommand=scrollbar.set)
        
        self.profile_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="保存当前账号", command=self.save_current_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="切换账号", command=self.on_switch_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除配置", command=self.delete_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新", command=self.refresh_all).pack(side=tk.RIGHT, padx=5)
        
        # 作者信息水印区域
        author_frame = ttk.LabelFrame(self.root, text="✨ 作者信息 ✨", padding=8)
        author_frame.pack(fill=tk.X, padx=10, pady=8)
        
        # 作者名称
        author_name = ttk.Label(
            author_frame, 
            text="👨‍💻 传康KK（万能程序员）",
            foreground='#e91e63',
            font=('PingFang SC', 12, 'bold')
        )
        author_name.pack(anchor=tk.W, pady=(0, 5))
        
        # 微信联系
        wechat_info = ttk.Label(
            author_frame,
            text="📱 微信：1837620622    📧 邮箱：2040168455@qq.com",
            foreground='#1a73e8',
            font=('PingFang SC', 10)
        )
        wechat_info.pack(anchor=tk.W, pady=2)
        
        # 平台信息
        platform_info = ttk.Label(
            author_frame,
            text="🎬 咸鱼/B站：万能程序员    ⭐ GitHub：github.com/1837620622",
            foreground='#666666',
            font=('PingFang SC', 10)
        )
        platform_info.pack(anchor=tk.W, pady=2)
        
        # Star提示
        star_info = ttk.Label(
            author_frame,
            text="🌟 开源免费，欢迎 Star 支持！",
            foreground='#ff9800',
            font=('PingFang SC', 10, 'bold')
        )
        star_info.pack(anchor=tk.W, pady=(5, 0))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪 | 开源免费，欢迎Star支持！")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    # --------------------------------------------------------
    # 账号信息读取
    # --------------------------------------------------------
    def get_current_account_info(self):
        """
        从state.vscdb数据库读取当前登录的账号信息
        返回:
            (name, email): 账号名称和邮箱的元组，失败返回(None, None)
        """
        try:
            if not os.path.exists(STATE_DB):
                return None, None
            
            conn = sqlite3.connect(STATE_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM ItemTable WHERE key='windsurfAuthStatus'")
            row = cursor.fetchone()
            conn.close()
            
            if row:
                data = json.loads(row[0])
                return data.get('name', '未知'), data.get('email', '未知')
            return None, None
        except Exception as e:
            print(f"读取账号信息失败: {e}")
            return None, None
    
    def show_current_account(self):
        """在界面上显示当前账号信息"""
        name, email = self.get_current_account_info()
        if name:
            self.current_account_label.config(text=f"👤 {name}")
            self.current_email_label.config(text=f"📧 {email}")
        else:
            self.current_account_label.config(text="未登录或无法读取")
            self.current_email_label.config(text="")
    
    # --------------------------------------------------------
    # Profile 列表管理
    # --------------------------------------------------------
    def refresh_profiles(self):
        """刷新Profile列表，从存储目录读取所有已保存的配置"""
        # 清空列表
        for item in self.profile_tree.get_children():
            self.profile_tree.delete(item)
        
        if not os.path.exists(PROFILES_DIR):
            return
        
        # 遍历Profile目录
        for profile_name in os.listdir(PROFILES_DIR):
            profile_path = os.path.join(PROFILES_DIR, profile_name)
            if os.path.isdir(profile_path):
                meta_file = os.path.join(profile_path, 'profile_meta.json')
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                        self.profile_tree.insert('', tk.END, values=(
                            profile_name,
                            meta.get('email', '未知'),
                            meta.get('saved_at', '未知')
                        ))
                    except:
                        self.profile_tree.insert('', tk.END, values=(profile_name, '读取失败', ''))
    
    def refresh_all(self):
        """刷新所有信息（当前账号和Profile列表）"""
        self.show_current_account()
        self.refresh_profiles()
        self.status_var.set("已刷新")
    
    # --------------------------------------------------------
    # 进程检测 (Mac版本)
    # --------------------------------------------------------
    def is_windsurf_running(self):
        """
        检查Windsurf是否正在运行 (Mac版本使用pgrep命令)
        返回:
            bool: True表示正在运行，False表示未运行
        """
        try:
            # 检查主进程
            result = subprocess.run(
                ['pgrep', '-f', 'Windsurf'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return True
            # 检查是否有 Windsurf Helper 进程
            result2 = subprocess.run(
                ['pgrep', '-f', 'Windsurf Helper'],
                capture_output=True, text=True
            )
            return result2.returncode == 0
        except:
            return False
    
    def force_quit_windsurf(self):
        """
        强制退出 Windsurf 进程
        """
        try:
            subprocess.run(['pkill', '-9', '-f', 'Windsurf'], capture_output=True)
            import time
            time.sleep(1)  # 等待进程完全退出
            return not self.is_windsurf_running()
        except:
            return False
    
    def verify_switch(self, expected_email):
        """
        验证账号切换是否成功
        参数:
            expected_email: 期望切换到的邮箱地址
        返回:
            bool: True表示切换成功，False表示失败
        """
        _, current_email = self.get_current_account_info()
        return current_email == expected_email
    
    # --------------------------------------------------------
    # 事件处理
    # --------------------------------------------------------
    def on_switch_click(self):
        """切换按钮点击事件处理"""
        try:
            self.status_var.set("正在切换...")
            self.root.update()  # 强制更新UI
            self.switch_profile()
        except Exception as e:
            messagebox.showerror("异常", f"切换过程发生异常:\n{e}")
            import traceback
            traceback.print_exc()
    
    # --------------------------------------------------------
    # 保存Profile
    # --------------------------------------------------------
    def save_current_profile(self):
        """保存当前账号为Profile配置"""
        # 检查 Windsurf 是否正在运行
        if self.is_windsurf_running():
            result = messagebox.askyesno(
                "警告", 
                "检测到 Windsurf 正在运行！\n\n"
                "为确保认证数据完整保存，建议先关闭 Windsurf。\n\n"
                "是否强制关闭 Windsurf 后继续？"
            )
            if result:
                self.status_var.set("正在关闭 Windsurf...")
                self.root.update()
                if not self.force_quit_windsurf():
                    messagebox.showerror("错误", "无法关闭 Windsurf，请手动关闭后重试")
                    return
            else:
                return
        
        name, email = self.get_current_account_info()
        if not name:
            messagebox.showerror("错误", "无法读取当前账号信息，请确保已登录Windsurf")
            return
        
        # 使用邮箱前缀作为默认配置名称
        default_name = email.split('@')[0] if email else "profile"
        profile_name = simpledialog.askstring("保存配置", "请输入配置名称:", initialvalue=default_name)
        
        if not profile_name:
            return
        
        # 清理非法字符，只保留字母、数字和部分符号
        profile_name = "".join(c for c in profile_name if c.isalnum() or c in ('_', '-', '.'))
        
        profile_path = os.path.join(PROFILES_DIR, profile_name)
        
        # 检查是否已存在同名配置
        if os.path.exists(profile_path):
            if not messagebox.askyesno("确认", f"配置 '{profile_name}' 已存在，是否覆盖？"):
                return
            shutil.rmtree(profile_path)
        
        try:
            os.makedirs(profile_path)
            
            # ★★★ 核心改进：复制整个 globalStorage 目录 ★★★
            global_storage_backup = os.path.join(profile_path, 'globalStorage')
            if os.path.exists(WINDSURF_GLOBAL_STORAGE):
                # 复制整个目录，排除大型备份文件
                shutil.copytree(
                    WINDSURF_GLOBAL_STORAGE, 
                    global_storage_backup,
                    ignore=shutil.ignore_patterns('*.backup.*', 'ms-*')
                )
            
            # 复制Session Storage
            if os.path.exists(SESSION_STORAGE):
                shutil.copytree(SESSION_STORAGE, os.path.join(profile_path, 'Session Storage'))
            
            # 复制Local Storage
            if os.path.exists(LOCAL_STORAGE):
                shutil.copytree(LOCAL_STORAGE, os.path.join(profile_path, 'Local Storage'))
            
            # 复制 Cookies 文件 (Mac 特有，认证关键文件)
            if os.path.exists(COOKIES_FILE):
                shutil.copy2(COOKIES_FILE, os.path.join(profile_path, 'Cookies'))
            if os.path.exists(COOKIES_JOURNAL):
                shutil.copy2(COOKIES_JOURNAL, os.path.join(profile_path, 'Cookies-journal'))
            
            # 复制 Network Persistent State 文件
            if os.path.exists(NETWORK_STATE_FILE):
                shutil.copy2(NETWORK_STATE_FILE, os.path.join(profile_path, 'Network Persistent State'))
            
            # 复制.codeium目录中的关键文件
            codeium_backup = os.path.join(profile_path, 'codeium')
            if os.path.exists(CODEIUM_DIR):
                # 只复制关键文件，不复制大型缓存
                os.makedirs(codeium_backup, exist_ok=True)
                for item in ['installation_id', 'user_settings.pb']:
                    src = os.path.join(CODEIUM_DIR, item)
                    if os.path.exists(src):
                        shutil.copy2(src, codeium_backup)
            
            # 保存元数据
            meta = {
                'name': name,
                'email': email,
                'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(os.path.join(profile_path, 'profile_meta.json'), 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            
            self.refresh_profiles()
            self.status_var.set(f"已保存配置: {profile_name}")
            messagebox.showinfo("成功", f"配置 '{profile_name}' 保存成功！\n\n已备份 globalStorage 完整目录。")
        
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    # --------------------------------------------------------
    # 切换Profile
    # --------------------------------------------------------
    def switch_profile(self):
        """切换到选中的Profile配置"""
        selected = self.profile_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要切换的配置")
            return
        
        # 获取选中的配置信息
        profile_name = str(self.profile_tree.item(selected[0])['values'][0])
        target_email = str(self.profile_tree.item(selected[0])['values'][1])
        profile_path = os.path.join(PROFILES_DIR, profile_name)
        
        print(f"[DEBUG] 切换操作开始")
        print(f"[DEBUG] profile_name: {profile_name}")
        print(f"[DEBUG] target_email: {target_email}")
        
        # 检查配置目录是否存在
        if not os.path.exists(profile_path):
            messagebox.showerror("错误", f"配置目录不存在: {profile_path}")
            return
        
        # 获取当前账号信息
        _, current_email = self.get_current_account_info()
        
        # 检查是否已经是目标账号
        if current_email == target_email:
            messagebox.showinfo("提示", f"当前已经是账号 '{target_email}'")
            return
        
        # 检查 Windsurf 是否正在运行
        if self.is_windsurf_running():
            result = messagebox.askyesno(
                "警告", 
                f"检测到 Windsurf 正在运行！\n\n"
                f"当前账号: {current_email}\n"
                f"目标账号: {target_email}\n\n"
                f"切换账号需要先关闭 Windsurf。\n\n"
                f"是否强制关闭 Windsurf 后继续切换？"
            )
            if result:
                self.status_var.set("正在关闭 Windsurf...")
                self.root.update()
                if not self.force_quit_windsurf():
                    messagebox.showerror("错误", "无法关闭 Windsurf，请手动关闭后重试")
                    return
            else:
                return
        else:
            # Windsurf 未运行，确认切换
            if not messagebox.askyesno("确认切换", f"当前账号: {current_email}\n目标账号: {target_email}\n\n确定要切换吗？"):
                return
        
        errors = []
        success_items = []
        
        # ★★★ 核心改进：检查并还原整个 globalStorage 目录 ★★★
        global_storage_backup = os.path.join(profile_path, 'globalStorage')
        if os.path.exists(global_storage_backup):
            try:
                # 删除现有的 globalStorage 目录
                if os.path.exists(WINDSURF_GLOBAL_STORAGE):
                    shutil.rmtree(WINDSURF_GLOBAL_STORAGE)
                # 复制备份的 globalStorage 目录
                shutil.copytree(global_storage_backup, WINDSURF_GLOBAL_STORAGE)
                success_items.append("globalStorage (完整目录)")
                print(f"[DEBUG] globalStorage 目录还原成功")
            except Exception as e:
                errors.append(f"globalStorage: {str(e)[:80]}")
                print(f"[DEBUG] globalStorage 还原失败: {e}")
        else:
            # 兼容旧版配置：只复制 state.vscdb
            state_backup = os.path.join(profile_path, 'state.vscdb')
            try:
                if os.path.exists(state_backup):
                    shutil.copy2(state_backup, STATE_DB)
                    success_items.append("state.vscdb")
            except Exception as e:
                errors.append(f"state.vscdb: {e}")
        
        # 2. 尝试复制Session Storage
        session_backup = os.path.join(profile_path, 'Session Storage')
        try:
            if os.path.exists(session_backup):
                if os.path.exists(SESSION_STORAGE):
                    shutil.rmtree(SESSION_STORAGE)
                shutil.copytree(session_backup, SESSION_STORAGE)
                success_items.append("Session Storage")
        except Exception as e:
            errors.append(f"Session Storage: {str(e)[:50]}")
        
        # 3. 尝试复制Local Storage
        local_backup = os.path.join(profile_path, 'Local Storage')
        try:
            if os.path.exists(local_backup):
                if os.path.exists(LOCAL_STORAGE):
                    shutil.rmtree(LOCAL_STORAGE)
                shutil.copytree(local_backup, LOCAL_STORAGE)
                success_items.append("Local Storage")
        except Exception as e:
            errors.append(f"Local Storage: {str(e)[:50]}")
        
        # 4. 复制 Cookies 文件 (Mac 认证关键)
        cookies_backup = os.path.join(profile_path, 'Cookies')
        cookies_journal_backup = os.path.join(profile_path, 'Cookies-journal')
        try:
            if os.path.exists(cookies_backup):
                shutil.copy2(cookies_backup, COOKIES_FILE)
                success_items.append("Cookies")
            if os.path.exists(cookies_journal_backup):
                shutil.copy2(cookies_journal_backup, COOKIES_JOURNAL)
        except Exception as e:
            errors.append(f"Cookies: {str(e)[:50]}")
        
        # 5. 复制 Network Persistent State 文件
        network_state_backup = os.path.join(profile_path, 'Network Persistent State')
        try:
            if os.path.exists(network_state_backup):
                shutil.copy2(network_state_backup, NETWORK_STATE_FILE)
                success_items.append("Network State")
        except Exception as e:
            errors.append(f"Network State: {str(e)[:50]}")
        
        # 6. 复制codeium配置文件
        codeium_backup = os.path.join(profile_path, 'codeium')
        try:
            if os.path.exists(codeium_backup):
                for item in os.listdir(codeium_backup):
                    src = os.path.join(codeium_backup, item)
                    dst = os.path.join(CODEIUM_DIR, item)
                    shutil.copy2(src, dst)
                success_items.append("codeium")
        except Exception as e:
            errors.append(f"codeium: {str(e)[:50]}")
        
        # 刷新显示
        self.show_current_account()
        self.root.update()
        
        # 验证切换结果
        _, new_email = self.get_current_account_info()
        print(f"[DEBUG] 切换后账号: {new_email}")
        
        if new_email == target_email:
            self.status_var.set(f"[OK] 切换成功: {profile_name}")
            msg = f"切换成功!\n\n当前账号: {target_email}\n\n成功复制: {', '.join(success_items)}"
            if errors:
                msg += f"\n\n部分文件复制失败(不影响使用):\n" + "\n".join(errors)
            msg += "\n\n请启动 Windsurf 验证。"
            messagebox.showinfo("切换成功", msg)
        else:
            self.status_var.set(f"[FAIL] 切换失败")
            msg = f"切换可能未完全成功\n\n期望: {target_email}\n显示: {new_email}\n\n已复制: {', '.join(success_items)}"
            if errors:
                msg += f"\n\n错误:\n" + "\n".join(errors)
            msg += "\n\n请启动 Windsurf 验证实际登录状态。"
            messagebox.showwarning("切换提示", msg)
    
    # --------------------------------------------------------
    # 删除Profile
    # --------------------------------------------------------
    def delete_profile(self):
        """删除选中的Profile配置"""
        selected = self.profile_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的配置")
            return
        
        # 转换为字符串，防止纯数字配置名导致的类型错误
        profile_name = str(self.profile_tree.item(selected[0])['values'][0])
        
        if not messagebox.askyesno("确认删除", f"确定要删除配置 '{profile_name}'？\n\n此操作不可恢复。"):
            return
        
        try:
            profile_path = os.path.join(PROFILES_DIR, profile_name)
            shutil.rmtree(profile_path)
            self.refresh_profiles()
            self.status_var.set(f"已删除配置: {profile_name}")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {e}")


# ============================================================
# 程序入口
# ============================================================
def main():
    """主函数，启动应用程序"""
    root = tk.Tk()
    
    # 设置样式主题
    style = ttk.Style()
    # Mac系统使用aqua主题获得原生外观
    try:
        style.theme_use('aqua')
    except:
        style.theme_use('clam')
    
    app = WindsurfAccountSwitcher(root)
    root.mainloop()


if __name__ == '__main__':
    main()
