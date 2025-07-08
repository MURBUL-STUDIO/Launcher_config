import os
import ctypes
import requests
import hashlib
import subprocess
import psutil
import time
import sys
import tempfile
import shutil

EXPECTED_HASHES = {
    "System32": "C1469DEA551C95D2C68EB42CEB37F020CB5B75D777E7083F24BF2E54AE2E4F55",
    "SysWOW64": "CEAE86E550DC1DAA1B364BE1AC195DD5DD9EAEA8BFDF1875A4AE832C3E1A42A2"
}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def download_file(url, dest):
    try:
        response = requests.get(url, verify=False, timeout=15)
        with open(dest, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return False

def force_unlock_file(file_path):
    """Улучшенная функция разблокировки файла"""
    try:
        # Закрываем процессы
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for f in proc.open_files():
                    if os.path.normpath(f.path).lower() == os.path.normpath(file_path).lower():
                        print(f"Закрываем процесс {proc.name()} (PID: {proc.pid})")
                        proc.kill()
                        time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Используем SID администраторов вместо имени группы
        subprocess.run(f'takeown /f "{file_path}" /A', shell=True, check=True)
        subprocess.run(f'icacls "{file_path}" /grant *S-1-5-32-544:F /T /C /Q', shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при назначении прав: {e}")
        # Пробуем через SYSTEM
        try:
            subprocess.run(f'psexec -s -i cmd /c "icacls \"{file_path}\" /grant *S-1-5-32-544:F /T /C /Q"', shell=True, check=True)
            return True
        except:
            return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False

def replace_dll(source_file, target_path):
    try:
        # Проверяем хэш скачанного файла
        file_hash = calculate_sha256(source_file)
        expected_hash = EXPECTED_HASHES["System32"] if "System32" in target_path else EXPECTED_HASHES["SysWOW64"]
        
        if file_hash.lower() != expected_hash.lower():
            print(f"Ошибка: Хэш не совпадает! Получено: {file_hash}, ожидалось: {expected_hash}")
            return False

        # Создаем временный файл
        temp_file = target_path + ".tmp"
        shutil.copy(source_file, temp_file)

        # Делаем бэкап
        backup_file = target_path + ".bak"
        if os.path.exists(backup_file):
            os.remove(backup_file)
        if os.path.exists(target_path):
            os.rename(target_path, backup_file)

        # Заменяем файл
        os.rename(temp_file, target_path)
        print(f"Файл {os.path.basename(target_path)} успешно заменен!")
        return True
    except Exception as e:
        print(f"Ошибка замены: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

def main():
    elevate()
    
    file_sources = {
        "System32": "https://github.com/MURBUL-STUDIO/windowssetupsdll2/raw/main/Windows.ApplicationModel.Store.dll",
        "SysWOW64": "https://github.com/MURBUL-STUDIO/windowssetupsdll/raw/main/Windows.ApplicationModel.Store.dll"
    }
    
    temp_dir = tempfile.mkdtemp()
    success = True
    
    try:
        for folder, url in file_sources.items():
            target_path = os.path.join(os.environ['WINDIR'], folder, "Windows.ApplicationModel.Store.dll")
            temp_file = os.path.join(temp_dir, f"{folder}_Windows.ApplicationModel.Store.dll")
            
            print(f"\n=== Обработка {folder} ===")
            
            # Скачивание
            print("1. Скачивание файла...")
            if not download_file(url, temp_file):
                success = False
                continue
            
            # Разблокировка
            print("2. Разблокировка файла...")
            if not force_unlock_file(target_path):
                print("Продолжаем попытку несмотря на ошибку прав...")
            
            # Замена
            print("3. Замена файла...")
            if not replace_dll(temp_file, target_path):
                success = False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    if success:
        print("\nОперация завершена. Для применения изменений требуется перезагрузка.")
        if input("Перезагрузить сейчас? (y/n): ").lower() == 'y':
            os.system("shutdown /r /t 5 /c 'Применение изменений DLL'")
    else:
        print("\nБыли ошибки. Проверьте логи выше.")

if __name__ == "__main__":
    # Отключаем предупреждения SSL
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Проверяем хэши
    if not all(EXPECTED_HASHES.values()):
        print("Ошибка: Укажите правильные хэши в EXPECTED_HASHES!")
        sys.exit(1)
    
    main()