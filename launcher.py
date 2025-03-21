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
        self.root.title("Game Launcher1")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)

        self.root.configure(bg="#2C3E50")

        self.main_frame = tk.Frame(root, bg="#2C3E50")
        self.main_frame.pack(fill="both", expand=True)

        # Загрузка конфигурации
        self.load_config()

        # Название игры слева сверху
        self.game_title = tk.Label(
            self.main_frame,
            text=self.config.get("game_title", "Моя Игра"),
            font=("Arial", 20, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        self.game_title.pack(side="top", anchor="nw", padx=20, pady=20)

        # Кнопка "Настройки" справа сверху
        self.settings_button = tk.Button(
            self.main_frame,
            text="Настройки",
            command=self.open_settings_menu,
            font=("Arial", 12, "bold"),
            bg="#3498DB",
            fg="white",
            width=10,
            height=1,
            relief="flat"
        )
        self.settings_button.pack(side="top", anchor="ne", padx=20, pady=20)

        # Меню настроек (на всю правую сторону, изначально скрыто)
        self.settings_menu = tk.Frame(self.root, bg="#34495E", width=300)
        self.settings_menu.place(relx=1.0, rely=0, anchor="ne", x=0, y=0, relheight=1.0)
        self.settings_menu_visible = False
        self.settings_menu.place_forget()

        # Кнопки в меню настроек
        self.reset_button = tk.Button(
            self.settings_menu,
            text="Сбросить обновление",
            command=self.reset_update,
            font=("Arial", 12),
            bg="#E74C3C",
            fg="white",
            width=20,
            relief="flat"
        )
        self.reset_button.pack(pady=10, padx=10)

        self.check_files_button = tk.Button(
            self.settings_menu,
            text="Локальные файлы",
            command=self.check_local_files,
            font=("Arial", 12),
            bg="#3498DB",
            fg="white",
            width=20,
            relief="flat"
        )
        self.check_files_button.pack(pady=10, padx=10)

        self.check_update_button = tk.Button(
            self.settings_menu,
            text="Проверить обновление",
            command=self.check_for_updates,
            font=("Arial", 12),
            bg="#2ECC71",
            fg="white",
            width=20,
            relief="flat"
        )
        self.check_update_button.pack(pady=10, padx=10)

        self.update_launcher_button = tk.Button(
            self.settings_menu,
            text="Обновить лаунчер",
            command=self.update_launcher,
            font=("Arial", 12),
            bg="#9B59B6",
            fg="white",
            width=20,
            relief="flat"
        )
        self.update_launcher_button.pack(pady=10, padx=10)

        # Кнопка "Закрыть" в меню настроек
        self.close_settings_button = tk.Button(
            self.settings_menu,
            text="Закрыть",
            command=self.close_settings_menu,
            font=("Arial", 12),
            bg="#E67E22",
            fg="white",
            width=20,
            relief="flat"
        )
        self.close_settings_button.pack(side="bottom", pady=20, padx=10)

        # Нижний фрейм для кнопок и статуса
        self.bottom_frame = tk.Frame(self.main_frame, bg="#2C3E50")
        self.bottom_frame.pack(side="bottom", fill="x")

        # Полоска другого цвета за кнопками
        self.strip = tk.Frame(self.bottom_frame, bg="#3498DB", height=100)
        self.strip.pack(side="left", fill="y")

        # Кнопка "Играть"
        self.start_button = tk.Button(
            self.strip,
            text="Играть",
            command=self.launch_game,
            font=("Arial", 16, "bold"),
            bg="#2980B9",
            fg="white",
            width=15,
            height=2,
            relief="flat"
        )
        self.start_button.pack(side="left", padx=20, pady=20)

        # Кнопка "Обновить" (меньше)
        self.update_button = tk.Button(
            self.strip,
            text="Обновить",
            command=self.download_update,
            font=("Arial", 12, "bold"),
            bg="#E67E22",
            fg="white",
            width=10,
            height=1,
            relief="flat",
            state="disabled"
        )
        self.update_button.pack(side="left", padx=10, pady=20)

        # Версия игры и статус
        self.version_label = tk.Label(
            self.bottom_frame,
            text="Версия: Неизвестно",
            font=("Arial", 14),
            bg="#2C3E50",
            fg="white"
        )
        self.version_label.pack(side="left", padx=20)

        self.status_label = tk.Label(
            self.bottom_frame,
            text="",
            font=("Arial", 12),
            bg="#2C3E50",
            fg="white"
        )
        self.status_label.pack(side="left", padx=10)

        # Кнопка выхода (крестик)
        self.exit_button = tk.Button(
            self.bottom_frame,
            text="X",
            command=self.quit,
            font=("Arial", 16, "bold"),
            bg="#E74C3C",
            fg="white",
            width=3,
            height=1,
            relief="flat"
        )
        self.exit_button.pack(side="right", padx=20, pady=20)

        # Прогресс-бар для обновлений
        self.progress = ttk.Progressbar(self.main_frame, length=400, mode="determinate")
        self.progress.pack(side="bottom", pady=20)
        self.progress.pack_forget()

        self.version_file = "version.json"
        self.game_path = "gamegg.py"
        self.launcher_path = "launcher.py"
        self.repo_base_url = "https://raw.githubusercontent.com/Laki031/my-game-updates/main"

        self.check_for_updates()

    def load_config(self):
        """Загрузка конфигурации лаунчера"""
        config_file = "launcher_config.json"
        self.config = {}
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {"game_title": "Моя Игра"}

    def open_settings_menu(self):
        """Открыть меню настроек"""
        self.settings_menu.place(relx=1.0, rely=0, anchor="ne", x=0, y=0, relheight=1.0)
        self.settings_menu_visible = True

    def close_settings_menu(self):
        """Закрыть меню настроек"""
        self.settings_menu.place_forget()
        self.settings_menu_visible = False

    def check_for_updates(self):
        """Проверка обновлений игры и лаунчера"""
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
                with open(self.version_file, "r") as f:
                    local_version_data = json.load(f)
                    local_game_version = int(local_version_data.get("game_version", 0))
                    local_launcher_version = int(local_version_data.get("launcher_version", 0))

            self.version_label.config(text=f"Версия игры: {local_game_version} | Лаунчер: {local_launcher_version}")

            if local_game_version < server_game_version:
                self.update_button.config(state="normal")
                self.status_label.config(text="Доступно обновление игры")
            elif local_launcher_version < server_launcher_version:
                self.status_label.config(text="Доступно обновление лаунчера")
            else:
                self.status_label.config(text="Все обновления установлены")
                self.update_button.config(state="disabled")

        except requests.RequestException:
            self.version_label.config(text="Версия: Неизвестно (нет сети)")
            self.status_label.config(text="Нет соединения")
            self.update_button.config(state="disabled")
        except (ValueError, KeyError):
            self.status_label.config(text="Ошибка в данных версии")

    def download_update(self):
        """Скачивание обновления игры с прогресс-баром"""
        try:
            self.progress.pack()
            self.progress["value"] = 0
            self.root.update()

            version_url = f"{self.repo_base_url}/version.json?{int(time.time())}"
            response = requests.get(version_url)
            response.raise_for_status()
            server_version_data = response.json()
            new_game_version = int(server_version_data["game_version"])

            self.progress["value"] = 33
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
                            self.progress["value"] = 33 + (downloaded / total_size * 67)
                            self.root.update()

            # Обновляем только версию игры
            with open(self.version_file, "r") as f:
                version_data = json.load(f)
            version_data["game_version"] = new_game_version
            with open(self.version_file, "w") as f:
                json.dump(version_data, f)

            self.version_label.config(
                text=f"Версия игры: {new_game_version} | Лаунчер: {version_data['launcher_version']}")
            self.update_button.config(state="disabled")
            self.status_label.config(text="Все обновления установлены")
            self.progress.pack_forget()

        except requests.RequestException as e:
            self.progress.pack_forget()
            self.status_label.config(text=f"Ошибка: {e}")
        except (ValueError, KeyError):
            self.progress.pack_forget()
            self.status_label.config(text="Ошибка в данных версии")

    def reset_update(self):
        """Сброс версии игры до 0"""
        if messagebox.askyesno("Сброс", "Сбросить версию игры до 0?"):
            version_data = {"game_version": 0, "launcher_version": 0}
            if os.path.exists(self.version_file):
                with open(self.version_file, "r") as f:
                    version_data = json.load(f)
            version_data["game_version"] = 0
            with open(self.version_file, "w") as f:
                json.dump(version_data, f)
            self.version_label.config(text=f"Версия игры: 0 | Лаунчер: {version_data['launcher_version']}")
            self.update_button.config(state="normal")
            self.status_label.config(text="Версия игры сброшена")

    def check_local_files(self):
        """Открытие папки с лаунчером"""
        folder_path = os.path.dirname(os.path.abspath(__file__))
        if os.name == "nt":  # Windows
            os.startfile(folder_path)
        elif os.name == "posix":  # Mac/Linux
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", folder_path])

    def update_launcher(self):
        """Обновление лаунчера с прогресс-баром"""
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
                with open(self.version_file, "r") as f:
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

                # Обновляем только версию лаунчера
                with open(self.version_file, "r") as f:
                    version_data = json.load(f)
                version_data["launcher_version"] = server_launcher_version
                with open(self.version_file, "w") as f:
                    json.dump(version_data, f)

                shutil.move("launcher_new.py", self.launcher_path)
                self.progress.pack_forget()
                self.version_label.config(
                    text=f"Версия игры: {version_data['game_version']} | Лаунчер: {server_launcher_version}")
                self.status_label.config(text="Лаунчер обновлен, перезапустите")
                self.root.quit()
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

    def quit(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()
