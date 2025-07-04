import os
import ctypes
import subprocess
import psutil
import time
import sys

def is_admin():
    """Проверяем, запущен ли скрипт от имени администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def take_ownership(file_path):
    """Получаем права владельца на файл с альтернативными методами"""
    try:
        # Пробуем стандартный метод
        subprocess.run(['takeown', '/f', file_path], check=True)
        
        # Альтернативный вариант для icacls (используем SID администраторов)
        subprocess.run([
            'icacls', file_path,
            '/grant', '*S-1-5-32-544:F',  # SID группы "Administrators"
            '/inheritance:r',
            '/T', '/C', '/Q'
        ], check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при получении прав: {e}")
        
        # Пробуем принудительно через SYSTEM
        try:
            subprocess.run([
                'psexec', '-i', '-s', 'cmd.exe', '/c',
                f'takeown /f "{file_path}" && icacls "{file_path}" /grant SYSTEM:F'
            ], check=True)
            return True
        except:
            return False

def kill_processes_locking_file(file_path):
    """Закрываем процессы, блокирующие файл"""
    killed = False
    file_path_lower = file_path.lower()
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for f in proc.open_files():
                if file_path_lower == f.path.lower():
                    print(f"Закрываем процесс {proc.name()} (PID: {proc.pid})")
                    proc.kill()
                    killed = True
                    time.sleep(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return killed

def rename_or_delete_file(file_path, action='rename'):
    """Пытаемся переименовать или удалить файл"""
    backup_path = file_path + '.bak'
    
    try:
        if action == 'rename':
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(file_path, backup_path)
            print(f"Файл успешно переименован в {backup_path}")
        else:
            os.remove(file_path)
            print("Файл успешно удален")
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def main():
    file_path = r"C:\Windows\System32\Windows.ApplicationModel.Store.dll"
    
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
    
    print("1. Пытаемся получить права на файл...")
    if not take_ownership(file_path):
        print("Не удалось получить права на файл. Пробуем альтернативные методы...")
        
        # Пробуем через TrustedInstaller
        try:
            subprocess.run([
                'sc', 'start', 'trustedinstaller',
                '&&', 'timeout', '/t', '3',
                '&&', 'takeown', '/f', file_path,
                '&&', 'icacls', file_path, '/grant', 'Administrators:F'
            ], shell=True, check=True)
        except:
            pass

    print("2. Проверяем блокирующие процессы...")
    if kill_processes_locking_file(file_path):
        print("Процессы, блокирующие файл, были закрыты")
        time.sleep(2)
    
    print("3. Пытаемся переименовать файл...")
    if not rename_or_delete_file(file_path, 'rename'):
        print("4. Пробуем удалить файл...")
        rename_or_delete_file(file_path, 'delete')

if __name__ == "__main__":
    main()
