import os
import ctypes
import subprocess
import psutil
import time
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def force_take_ownership(file_path):
    """Принудительное получение прав через несколько методов"""
    methods = [
        # Метод 1: Стандартный takeown + icacls
        lambda: subprocess.run(f'takeown /f "{file_path}" && icacls "{file_path}" /grant *S-1-5-32-544:F /inheritance:r', shell=True, check=True),
        
        # Метод 2: Через PsExec от SYSTEM
        lambda: subprocess.run(f'psexec -s -i cmd /c "takeown /f "{file_path}" && icacls "{file_path}" /grant SYSTEM:F"', shell=True, check=True),
        
        # Метод 3: Через TrustedInstaller
        lambda: subprocess.run(
            'sc start TrustedInstaller && ' +
            'timeout /t 3 && ' +
            f'takeown /f "{file_path}" && ' +
            f'icacls "{file_path}" /grant *S-1-5-32-544:F',
            shell=True, check=True)
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            print(f"Попытка {i}...")
            method()
            return True
        except subprocess.CalledProcessError as e:
            print(f"Метод {i} не сработал: {e}")
    return False

def kill_all_lockers(file_path):
    """Закрытие всех процессов, использующих файл"""
    file_path_lower = os.path.normpath(file_path).lower()
    killed = False
    
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
        try:
            # Пропускаем критические процессы
            if proc.username() in ('SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE'):
                continue
                
            for f in proc.open_files():
                if os.path.normpath(f.path).lower() == file_path_lower:
                    print(f"Закрываем {proc.name()} (PID: {proc.pid})")
                    proc.kill()
                    killed = True
                    time.sleep(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return killed

def secure_file_operation(file_path):
    """Безопасные операции с файлом"""
    backup_path = file_path + '.bak'
    
    # Метод 1: Простое переименование
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(file_path, backup_path)
        print(f"Файл переименован: {backup_path}")
        return True
    except Exception as e:
        print(f"Переименование не удалось: {e}")
    
    # Метод 2: Удаление через move (иногда работает когда rename нет)
    try:
        subprocess.run(f'move /Y "{file_path}" "{backup_path}"', shell=True, check=True)
        print(f"Файл перемещен: {backup_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Перемещение не удалось: {e}")
    
    # Метод 3: Нулевое замещение
    try:
        with open(file_path, 'wb') as f:
            f.truncate()
        os.remove(file_path)
        print("Файл обнулен и удален")
        return True
    except Exception as e:
        print(f"Обнуление не удалось: {e}")
    
    return False

def main():
    target_file = r"C:\Windows\SysWOW64\Windows.ApplicationModel.Store.dll"
    
    if not os.path.exists(target_file):
        print("Файл не найден!")
        return
    
    elevate()
    print(f"Обработка: {target_file}")
    
    # Этап 1: Получение прав
    print("\n[1/3] Получаем права...")
    if force_take_ownership(target_file):
        print("Права получены!")
    else:
        print("Не удалось получить права. Продолжаем попытки...")
    
    # Этап 2: Закрытие процессов
    print("\n[2/3] Закрываем процессы...")
    if kill_all_lockers(target_file):
        print("Процессы закрыты!")
    else:
        print("Не найдено процессов или не удалось закрыть")
    
    # Этап 3: Работа с файлом
    print("\n[3/3] Модифицируем файл...")
    if secure_file_operation(target_file):
        print("Операция успешна!")
    else:
        print("\nВсе методы не сработали.")
        

if __name__ == "__main__":
    # Дополнительные меры перед запуском
    os.system('taskkill /f /im dllhost.exe /im mmc.exe >nul 2>&1')
    main()
