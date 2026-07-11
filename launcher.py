"""
Gamemie Launcher / Installer
Build to .exe with:  pyinstaller --onefile --noconsole --name GamemieLauncher launcher.py
"""

import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import os
import zipfile
import shutil
import urllib.request

# ── CONFIG ────────────────────────────────────────────────────────────────────
REPO_ZIP_URL      = "https://github.com/shukachi/gamemie/archive/refs/heads/prod.zip"
PYTHON_DL_URL     = "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe"
INSTALL_DIR       = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Gamemie")
DESKTOP_DIR       = os.path.join(os.path.expanduser("~"), "Desktop")
REQUIRED_PACKAGES = ["arcade", "Pillow"]

# ── COLOURS ───────────────────────────────────────────────────────────────────
C_BG     = "#0f0f17"
C_PANEL  = "#16161f"
C_FG     = "#d4d4d4"
C_ACCENT = "#c8a84b"
C_GREEN  = "#4caf70"
C_DIM    = "#555566"
C_ERR    = "#cc4444"
C_BTN    = "#22223a"
C_BTN_A  = "#2e2e50"


# ── PYTHON DETECTION ─────────────────────────────────────────────────────────

def find_python() -> str | None:
    """Return path to Python 3.10+ executable, or None."""
    candidates = ["python", "python3", "py"]
    for c in candidates:
        exe = shutil.which(c)
        if exe and _python_ok(exe):
            return exe
    # Common Windows install paths
    local = os.environ.get("LOCALAPPDATA", "")
    extra = [
        r"C:\Python312\python.exe",
        r"C:\Python311\python.exe",
        r"C:\Python310\python.exe",
        os.path.join(local, "Programs", "Python", "Python312", "python.exe"),
        os.path.join(local, "Programs", "Python", "Python311", "python.exe"),
        os.path.join(local, "Programs", "Python", "Python310", "python.exe"),
    ]
    for path in extra:
        if os.path.isfile(path) and _python_ok(path):
            return path
    return None


def _python_ok(exe: str) -> bool:
    try:
        r = subprocess.run(
            [exe, "-c", "import sys; exit(0 if sys.version_info>=(3,10) else 1)"],
            capture_output=True, timeout=6
        )
        return r.returncode == 0
    except Exception:
        return False


# ── MAIN WINDOW ───────────────────────────────────────────────────────────────

class LauncherApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Gamemie")
        self.geometry("460x330")
        self.resizable(False, False)
        self.configure(bg=C_BG)
        self._center()
        self._apply_style()
        self._show_install_screen()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 460) // 2
        y = (self.winfo_screenheight() - 330) // 2
        self.geometry(f"460x330+{x}+{y}")

    def _apply_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Dark.Horizontal.TProgressbar",
                    troughcolor=C_PANEL, background=C_ACCENT,
                    bordercolor=C_BG, lightcolor=C_ACCENT, darkcolor=C_ACCENT)

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ── INSTALL SCREEN ────────────────────────────────────────────────────────

    def _show_install_screen(self):
        self._clear()

        tk.Label(self, text="GAMEMIE", fg=C_ACCENT, bg=C_BG,
                 font=("Consolas", 30, "bold")).pack(pady=(30, 2))
        tk.Label(self, text="Arcade  Club", fg=C_DIM, bg=C_BG,
                 font=("Consolas", 11)).pack()

        sep = tk.Frame(self, bg=C_DIM, height=1, width=360)
        sep.pack(pady=(18, 0))

        # Shortcut checkbox
        self._shortcut_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self,
            text="  Создать ярлык на рабочем столе",
            variable=self._shortcut_var,
            fg=C_FG, bg=C_BG,
            selectcolor="#1e1e2e",
            activeforeground=C_FG, activebackground=C_BG,
            font=("Consolas", 10), cursor="hand2"
        ).pack(pady=(14, 0))

        # Install button
        self._btn = tk.Button(
            self, text="УСТАНОВИТЬ",
            command=self._start_install,
            bg=C_BTN, fg=C_ACCENT,
            activebackground=C_BTN_A, activeforeground=C_ACCENT,
            font=("Consolas", 13, "bold"),
            relief="flat", padx=30, pady=9, cursor="hand2", bd=0
        )
        self._btn.pack(pady=(14, 0))

        self._progress = ttk.Progressbar(
            self, length=360, mode="indeterminate",
            style="Dark.Horizontal.TProgressbar"
        )
        self._progress.pack(pady=(16, 0))

        self._status = tk.Label(self, text="", fg=C_DIM, bg=C_BG,
                                font=("Consolas", 9))
        self._status.pack(pady=(6, 0))

    # ── DONE SCREEN ───────────────────────────────────────────────────────────

    def _show_done_screen(self, game_dir: str, shortcut_ok: bool):
        self._clear()
        self.geometry("460x330")

        tk.Label(self, text="GAMEMIE", fg=C_ACCENT, bg=C_BG,
                 font=("Consolas", 30, "bold")).pack(pady=(30, 2))
        tk.Label(self, text="Установлено  ✓", fg=C_GREEN, bg=C_BG,
                 font=("Consolas", 11)).pack()

        sep = tk.Frame(self, bg=C_DIM, height=1, width=360)
        sep.pack(pady=(14, 10))

        if shortcut_ok:
            tk.Label(self, text="Ярлык «Gamemie» появился на рабочем столе.",
                     fg=C_DIM, bg=C_BG, font=("Consolas", 9)).pack()
        else:
            tk.Label(self, text="Чтобы запустить игру, откройте терминал и введите:",
                     fg=C_DIM, bg=C_BG, font=("Consolas", 9)).pack()
            box = tk.Frame(self, bg="#141420", padx=12, pady=7)
            box.pack(fill="x", padx=50, pady=(5, 0))
            tk.Label(box,
                     text=f'cd "{game_dir}"\npython main.py',
                     fg="#88aacc", bg="#141420",
                     font=("Consolas", 9), justify="left").pack(anchor="w")

        tk.Button(
            self, text="▶  ЗАПУСТИТЬ ИГРУ",
            command=lambda: self._launch_game(game_dir),
            bg="#142814", fg=C_GREEN,
            activebackground="#1e3c1e", activeforeground=C_GREEN,
            font=("Consolas", 13, "bold"),
            relief="flat", padx=28, pady=9, cursor="hand2", bd=0
        ).pack(pady=(18, 0))

        tk.Button(
            self, text="Закрыть",
            command=self.quit,
            bg=C_BG, fg=C_DIM,
            activebackground=C_BG, activeforeground="#888",
            font=("Consolas", 9), relief="flat", bd=0, cursor="hand2"
        ).pack(pady=(8, 0))

    # ── ERROR STATE ───────────────────────────────────────────────────────────

    def _show_error(self, msg: str):
        self._progress.stop()
        self._status.config(text=f"Ошибка: {msg[:72]}", fg=C_ERR)
        self._btn.config(state="normal", text="ПОВТОРИТЬ")

    # ── INSTALL THREAD ────────────────────────────────────────────────────────

    def _set_status(self, text: str):
        self.after(0, lambda: self._status.config(text=text, fg=C_DIM)
                   if hasattr(self, "_status") else None)

    def _start_install(self):
        self._btn.config(state="disabled")
        self._progress.start(12)
        threading.Thread(target=self._install_thread, daemon=True).start()

    def _install_thread(self):
        try:
            # ── Step 1: Python ────────────────────────────────────────────────
            self._set_status("Поиск Python...")
            python = find_python()
            if not python:
                self._set_status("Загрузка Python 3.12  (≈27 МБ)…")
                python = self._download_and_install_python()
            if not python:
                raise RuntimeError("Не удалось найти или установить Python 3.10+")

            # ── Step 2: Download game ─────────────────────────────────────────
            self._set_status("Загрузка игры…")
            tmp_zip = os.path.join(os.environ.get("TEMP", ""), "gamemie_src.zip")
            urllib.request.urlretrieve(REPO_ZIP_URL, tmp_zip, self._dl_hook)

            # ── Step 3: Extract ───────────────────────────────────────────────
            self._set_status("Распаковка…")
            os.makedirs(INSTALL_DIR, exist_ok=True)
            with zipfile.ZipFile(tmp_zip, "r") as z:
                z.extractall(INSTALL_DIR)
            try:
                os.remove(tmp_zip)
            except OSError:
                pass

            # GitHub puts files inside "gamemie-prod/" subfolder
            game_dir = INSTALL_DIR
            for name in os.listdir(INSTALL_DIR):
                candidate = os.path.join(INSTALL_DIR, name)
                if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "main.py")):
                    game_dir = candidate
                    break

            # ── Step 4: pip install ───────────────────────────────────────────
            self._set_status("Установка зависимостей…")
            subprocess.run(
                [python, "-m", "pip", "install", "--quiet", "--upgrade"] + REQUIRED_PACKAGES,
                check=True, capture_output=True
            )

            # ── Step 5: Shortcut ──────────────────────────────────────────────
            shortcut_ok = False
            if self._shortcut_var.get():
                self._set_status("Создание ярлыка…")
                shortcut_ok = _create_desktop_shortcut(python, game_dir)

            self.after(0, self._show_done_screen, game_dir, shortcut_ok)

        except Exception as exc:
            self.after(0, self._show_error, str(exc))

    def _dl_hook(self, block_num, block_size, total):
        if total > 0:
            pct = min(100, block_num * block_size * 100 // total)
            self._set_status(f"Загрузка игры…  {pct}%")

    def _download_and_install_python(self) -> str | None:
        tmp = os.path.join(os.environ.get("TEMP", ""), "python_setup.exe")
        try:
            urllib.request.urlretrieve(PYTHON_DL_URL, tmp)
            subprocess.run(
                [tmp, "/quiet", "InstallAllUsers=0",
                 "PrependPath=1", "Include_test=0", "Include_launcher=0"],
                check=True
            )
        except Exception:
            return None
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass
        return find_python()

    # ── LAUNCH ────────────────────────────────────────────────────────────────

    def _launch_game(self, game_dir: str):
        python = find_python()
        if python:
            subprocess.Popen([python, "main.py"], cwd=game_dir)
        self.quit()


# ── SHORTCUT HELPER ───────────────────────────────────────────────────────────

def _create_desktop_shortcut(python_exe: str, game_dir: str) -> bool:
    main_py = os.path.join(game_dir, "main.py")
    lnk     = os.path.join(DESKTOP_DIR, "Gamemie.lnk")
    # Escape backslashes for PowerShell string
    p  = python_exe.replace("\\", "\\\\")
    m  = main_py.replace("\\", "\\\\")
    wd = game_dir.replace("\\", "\\\\")
    ps = (
        f'$ws = New-Object -ComObject WScript.Shell; '
        f'$s = $ws.CreateShortcut("{lnk}"); '
        f'$s.TargetPath = "{p}"; '
        f'$s.Arguments = "\\"{m}\\""; '
        f'$s.WorkingDirectory = "{wd}"; '
        f'$s.Description = "Gamemie Arcade Club"; '
        f'$s.Save()'
    )
    try:
        subprocess.run(["powershell", "-Command", ps],
                       capture_output=True, check=True, timeout=15)
        return True
    except Exception:
        return False


# ── ENTRY ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
