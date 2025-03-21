import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import sys
import os
import requests
import time
import json
import shutil

class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Launcher")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        
        self.root.configure(bg="#1A2525")
        
        self.main_frame = tk.Frame(root, bg="#1A2525")
        self.main_frame.pack(fill="both", expand=True)
        
        self.main_frame.bind("<Button-1>", self.start_drag)
        self.main_frame.bind("<B1-Motion>", self.on_drag)
        
        self.load_config()
        
        self.game_title = tk.Label(
            self.main_frame,
            text=self.config.get("game_title", "Моя Игра"),
            font=("Arial", 20, "bold"),
            bg="#1A2525",
            fg="#D9E6E6"
        )
        self.game_title.pack(side="top", anchor="nw", padx=20, pady=10)
        self.game_title.bind("<Button-1>", self.start_drag)
        self.game_title.bind("<B1-Motion>", self.on_drag)
        
        self.settings_button = tk.Button(
            self.main_frame,
            text="Настройки",
            command=self.open_settings_menu,
            font=("Arial", 12, "bold"),
            bg="#2A3F3F",
            fg="#D9E6E6",
            width=10,
            height=1,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            activebackground="#3A5F5F"
        )
        self.settings_button.pack(side="top", anchor="ne", padx=20, pady=10)
        self.settings_button.config(border=10)
        
        self.settings_menu = tk.Frame(self.root, bg="#263333", width=300)
        self.settings_menu.place(relx=1.0, rely=0, anchor="ne", x=0, y=0, relheight=1.0)
        self.settings_menu_visible = False
        self.settings_menu.place_forget()
        
        self.reset_button = tk.Button(self.settings_menu, text="Сбросить обновление", command=self.reset_update, font=("Arial", 12), bg="#4A2A2A", fg="#D9E6E6", width=20, relief="flat", borderwidth=0, highlightthickness=0, activebackground="#6A3A3A")
        self.reset_button.pack(pady=10, padx=10)
        self.reset_button.config(border=10)
        
        self.check_files_button = tk.Button(self.settings_menu, text="Локальные файлы", command=self.check_local_files, font=("Arial", 12), bg="#2A3F3F", fg="#D9E6E6", width=20, relief="flat", borderwidth=0, highlightthickness=0, activebackground="#3A5F5F")
        self.check_files_button.pack(pady=10, padx=10)
        self.check_files_button.config(border=10)
        
        self.check_update_button = tk.Button(self.settings_menu, text="Проверить обновление", command=self.check_for_updates, font=("Arial", 12), bg="#2A4A2A", fg="#D9E6E6", width=20, relief="flat", borderwidth=0, highlightthickness=0, activebackground="#3A6A3A")
        self.check_update_button.pack(pady=10, padx=10)
        self.check_update_button.config(border=10)
        
        self.update_launcher_button = tk.Button(self.settings_menu, text="Обновить лаунчер", command=self.update_launcher, font=("Arial", 12), bg="#3F2A4A", fg="#D9E6E6", width=20, relief="flat", borderwidth=0, highlightthickness=0, activebackground="#5F3A6A")
        self.update_launcher_button.pack(pady=10, padx=10)
        self.update_launcher_button.config(border=10)
        
        self.map_editor_button = tk.Button(self.settings_menu, text="Редактор карты", command=self.launch_map_editor, font=("Arial", 12), bg="#2A3F4A", fg="#D9E6E6", width=20, relief="flat", borderwidth=0, highlightthickness=0, activebackground="#3A5F6A")
        self.map_editor_button.pack(pady=10, padx=10)
        self.map_editor_button.config(border=10)
        
        self.close_settings_button = tk.Button(self.settings_menu, text="Закрыть", command=self.close_settings_menu, font=("Arial", 12), bg="#4A3F2A", fg="#D9E6E6", width=20, relief="flat", borderwidth=0, highlightthickness=0, activebackground="#6A5F3A")
        self.close_settings_button.pack(side="bottom", pady=20, padx=10)
        self.close_settings_button.config(border=10)
        
        self.changelog_frame = tk.Frame(self.main_frame, bg="#2A3F3F", height=200)
        self.changelog_frame.pack(side="top", fill="x", padx=20, pady=10)
        
        self.changelog_title = tk.Label(self.changelog_frame, text=f"Новая версия: {self.get_latest_game_version()}", font=("Arial", 14, "bold"), bg="#2A3F3F", fg="#D9E6E6")
        self.changelog_title.pack(pady=5)
        
        changelog_text = "\n".join(self.config.get("changelog", ["- Нет данных об изменениях"]))
        self.changelog_label = tk.Label(self.changelog_frame, text=changelog_text, font=("Arial", 12), bg="#2A3F3F", fg="#D9E6E6", justify="left")
        self.changelog_label.pack(pady=5)
        
        self.bottom_frame = tk.Frame(self.main_frame, bg="#1A2525")
        self.bottom_frame.pack(side="bottom", fill="x")
        
        self.strip = tk.Frame(self.bottom_frame, bg="#2A3F3F", height=100)
        self.strip.pack(side="top", fill="x")
        
        self.start_button = tk.Button(self.strip, text="Играть", command=self.launch_game, font=("Arial", 16, "bold"), bg="#1F4A4A", fg="#D9E6E6", width=15, height=2, relief="flat", borderwidth=0, highlightthickness=0, activebackground="#2F6A6A")
        self.start_button.pack(side="left", padx=20, pady=20)
        self.start_button.config(border=15)
        
        self.version_label = tk.Label(self.bottom_frame, text="Версия: Неизвестно", font=("Arial", 14), bg="#1A2525", fg="#D9E6E6")
        self.version_label.pack(side="left", padx=20)
        
        self.status_label = tk.Label(self.bottom_frame, text="", font=("Arial", 12), bg="#1A2525", fg="#D9E6E6")
        self.status_label.pack(side="left", padx=10)
        
        self.exit_button = tk.Button(self.bottom_frame, text="X", command=self.quit, font=("Arial", 16, "bold"), bg="#4A2A2A", fg="#D9E6E6", width=3, height=1, relief="flat", borderwidth=0, highlightthickness=0, activebackground="#6A3A3A")
        self.exit_button.pack(side="right", padx=20, pady=20)
        self.exit_button.config(border=10)
        
        self.progress = ttk.Progressbar(self.bottom_frame, length=400, mode="determinate")
        self.progress.pack(side="bottom", pady=10)
        self.progress.pack_forget()
        
        self.version_file = "version.json"
        self.game_path = "gamegg.py"
        self.editor_path = "redactor.py"
        self.launcher_path = "launcher.py"
        self.repo_base_url = "https://raw.githubusercontent.com/Laki031/my-game-updates/main"
        
        self.check_for_updates()

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def load_config(self):
        config_file = "launcher_config.json"
        self.config = {"game_title": "Моя Игра", "changelog": ["- Нет данных об изменениях"]}
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)

    def get_latest_game_version(self):
        try:
            version_url = f"{self.repo_base_url}/version.json?{int(time.time())}"
            response = requests.get(version_url)
            response.raise_for_status()
            return response.json()["game_version"]
        except:
            return "Неизвестно"

    def open_settings_menu(self):
        self.settings_menu.place(relx=1.0, rely=0, anchor="ne", x=0, y=0, relheight=1.0)
        self.settings_menu_visible = True

    def close_settings_menu(self):
        self.settings_menu.place_forget()
        self.settings_menu_visible = False

    def check_for_updates(self):
        try:
            version_url = f"{self.repo_base_url}/version.json?{int(time.time())}"
            response = requests.get(version_url)
            response.raise_for_status()
            server_version_data = response.json()
            server_game_version = int(server_version_data["game_version"])
            server_launcher_version = int(server_version_data["launcher_version"])
            
            local_game_version = 0
            local_launcher_version = 0
            if os.path.exists(self.version_file):
                with open(self.version_file, "r", encoding="utf-8") as f:
                    local_version_data = json.load(f)
                    local_game_version = int(local_version_data.get("game_version", 0))
                    local_launcher_version = int(local_version_data.get("launcher_version", 0))
            
            self.version_label.config(text=f"Версия игры: {local_game_version} | Лаунчер: {local_launcher_version}")
            self.changelog_title.config(text=f"Новая версия: {server_game_version}")
            
            if local_game_version < server_game_version:
                self.download_update()  # Автоматическое обновление
            elif local_launcher_version < server_launcher_version:
                self.status_label.config(text="Доступно обновление лаунчера")
            else:
                self.status_label.config(text="Все обновления установлены")
                
        except requests.RequestException:
            self.version_label.config(text="Версия: Неизвестно (нет сети)")
            self.status_label.config(text="Нет соединения")
        except (ValueError, KeyError):
            self.status_label.config(text="Ошибка в данных версии")

    def download_update(self):
        try:
            self.progress.pack()
            self.progress["value"] = 0
            self.root.update()
            
            version_url = f"{self.repo_base_url}/version.json?{int(time.time())}"
            response = requests.get(version_url)
            response.raise_for_status()
            server_version_data = response.json()
            new_game_version = int(server_version_data["game_version"])
            
            self.progress["value"] = 20
            self.root.update()
            time.sleep(0.5)
            
            game_url = f"{self.repo_base_url}/gamegg.py?{int(time.time())}"
            response = requests.get(game_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            with open(self.game_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.progress["value"] = 20 + (downloaded / total_size * 40)
                            self.root.update()
            
            self.progress["value"] = 60
            self.root.update()
            time.sleep(0.5)
            
            editor_url = f"{self.repo_base_url}/redactor.py?{int(time.time())}"
            response = requests.get(editor_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            with open(self.editor_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.progress["value"] = 60 + (downloaded / total_size * 40)
                            self.root.update()
            
            with open(self.version_file, "r", encoding="utf-8") as f:
                version_data = json.load(f)
            version_data["game_version"] = new_game_version
            with open(self.version_file, "w", encoding="utf-8") as f:
                json.dump(version_data, f)
            
            config_url = f"{self.repo_base_url}/launcher_config.json?{int(time.time())}"
            response = requests.get(config_url)
            if response.status_code == 200:
                with open("launcher_config.json", "wb") as f:
                    f.write(response.content)
                self.load_config()
                self.game_title.config(text=self.config.get("game_title", "Моя Игра"))
                changelog_text = "\n".join(self.config.get("changelog", ["- Нет данных об изменениях"]))
                self.changelog_label.config(text=changelog_text)
            
            self.version_label.config(text=f"Версия игры: {new_game_version} | Лаунчер: {version_data['launcher_version']}")
            self.status_label.config(text="Все обновления установлены")
            self.progress.pack_forget()
            
        except requests.RequestException as e:
            self.progress.pack_forget()
            self.status_label.config(text=f"Ошибка: {e}")
        except (ValueError, KeyError):
            self.progress.pack_forget()
            self.status_label.config(text="Ошибка в данных версии")

    def reset_update(self):
        if messagebox.askyesno("Сброс", "Сбросить версию игры до 0?"):
            version_data = {"game_version": 0, "launcher_version": 0}
            if os.path.exists(self.version_file):
                with open(self.version_file, "r", encoding="utf-8") as f:
                    version_data = json.load(f)
            version_data["game_version"] = 0
            with open(self.version_file, "w", encoding="utf-8") as f:
                json.dump(version_data, f)
            self.version_label.config(text=f"Версия игры: 0 | Лаунчер: {version_data['launcher_version']}")
            self.status_label.config(text="Версия игры сброшена")

    def check_local_files(self):
        folder_path = os.path.dirname(os.path.abspath(__file__))
        if os.name == "nt":
            os.startfile(folder_path)
        elif os.name == "posix":
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", folder_path])

    def update_launcher(self):
        try:
            self.progress.pack()
            self.progress["value"] = 0
            self.root.update()
            
            version_url = f"{self.repo_base_url}/version.json?{int(time.time())}"
            response = requests.get(version_url)
            response.raise_for_status()
            server_version_data = response.json()
            server_launcher_version = int(server_version_data["launcher_version"])
            
            local_launcher_version = 0
            if os.path.exists(self.version_file):
                with open(self.version_file, "r", encoding="utf-8") as f:
                    local_data = json.load(f)
                    local_launcher_version = int(local_data["launcher_version"])
            
            self.progress["value"] = 33
            self.root.update()
            time.sleep(0.5)
            
            if local_launcher_version < server_launcher_version:
                launcher_url = f"{self.repo_base_url}/launcher.py?{int(time.time())}"
                response = requests.get(launcher_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0
                with open("launcher_new.py", "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                self.progress["value"] = 33 + (downloaded / total_size * 67)
                                self.root.update()
                
                config_url = f"{self.repo_base_url}/launcher_config.json?{int(time.time())}"
                response = requests.get(config_url)
                if response.status_code == 200:
                    with open("launcher_config.json", "wb") as f:
                        f.write(response.content)
                
                with open(self.version_file, "r", encoding="utf-8") as f:
                    version_data = json.load(f)
                version_data["launcher_version"] = server_launcher_version
                with open(self.version_file, "w", encoding="utf-8") as f:
                    json.dump(version_data, f)
                
                shutil.move("launcher_new.py", self.launcher_path)
                self.progress.pack_forget()
                self.version_label.config(text=f"Версия игры: {version_data['game_version']} | Лаунчер: {server_launcher_version}")
                self.status_label.config(text="Лаунчер обновлен, перезапускается...")
                self.root.update()
                time.sleep(1)
                os.execv(sys.executable, [sys.executable, self.launcher_path])
            else:
                self.progress.pack_forget()
                self.status_label.config(text="Все обновления установлены")
                
        except requests.RequestException as e:
            self.progress.pack_forget()
            self.status_label.config(text=f"Ошибка: {e}")
        except (ValueError, KeyError):
            self.progress.pack_forget()
            self.status_label.config(text="Ошибка в данных версии")

    def launch_game(self):
        if not os.path.exists(self.game_path):
            self.status_label.config(text="Файл игры не найден")
            return
        
        try:
            process = subprocess.Popen([sys.executable, self.game_path])
            time.sleep(3)
            if process.poll() is None:
                self.root.quit()
            else:
                self.status_label.config(text="Игра завершилась неожиданно")
        except Exception as e:
            self.status_label.config(text=f"Ошибка запуска: {e}")

    def launch_map_editor(self):
        if not os.path.exists(self.editor_path):
            self.status_label.config(text="Файл редактора не найден")
            return
        
        try:
            process = subprocess.Popen([sys.executable, self.editor_path])
            time.sleep(3)
            if process.poll() is None:
                self.root.quit()
            else:
                self.status_label.config(text="Редактор завершился неожиданно")
        except Exception as e:
            self.status_label.config(text=f"Ошибка запуска редактора: {e}")

    def quit(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()
