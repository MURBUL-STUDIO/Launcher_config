import os
import ctypes
import urllib.request
import ssl
import shutil
import subprocess
import sys
import tempfile
import requests

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def download_file(url, dest):
    try:
        # Метод 1: Попробовать с отключенной проверкой SSL
        ssl_context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=ssl_context) as response, open(dest, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print(f"Метод 1 не сработал: {e}")
        try:
            # Метод 2: Использовать requests с отключенной проверкой SSL
            response = requests.get(url, verify=False, timeout=10)
            with open(dest, 'wb') as out_file:
                out_file.write(response.content)
            return True
        except Exception as e:
            print(f"Метод 2 не сработал: {e}")
            return False

def verify_file(file_path):
    """Проверяем что файл является валидным DLL"""
    try:
        if not file_path.endswith('.dll'):
            return False
        if os.path.getsize(file_path) < 1024:  # Минимальный размер для DLL
            return False
        
        # Дополнительная проверка сигнатуры PE-файла
        with open(file_path, 'rb') as f:
            if f.read(2) != b'MZ':  # PE-сигнатура
                return False
        return True
    except:
        return False

def replace_system_file(src_file, dest_path):
    """Безопасная замена системного файла"""
    try:
        # 1. Создаем временную копию в целевой папке
        temp_file = os.path.join(os.path.dirname(dest_path), "temp_" + os.path.basename(dest_path))
        shutil.copy(src_file, temp_file)
        
        # 2. Проверяем новую версию
        if not verify_file(temp_file):
            os.remove(temp_file)
            return False
        
        # 3. Делаем бэкап оригинального файла
        backup_file = dest_path + ".bak"
        if os.path.exists(dest_path):
            if os.path.exists(backup_file):
                os.remove(backup_file)
            os.rename(dest_path, backup_file)
        
        # 4. Заменяем файл
        os.rename(temp_file, dest_path)
        
        # 5. Восстанавливаем права
        subprocess.run(f'icacls "{dest_path}" /inheritance:r /grant *S-1-5-32-544:F', shell=True)
        return True
    except Exception as e:
        print(f"Ошибка замены файла: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

def main():
    elevate()
    
    # Источники файлов
    file_sources = {
        "System32": "https://github.com/MURBUL-STUDIO/windowssetupsdll2/raw/main/Windows.ApplicationModel.Store.dll",
        "SysWOW64": "https://github.com/MURBUL-STUDIO/windowssetupsdll/raw/main/Windows.ApplicationModel.Store.dll"
    }
    
    # Альтернативные источники (если основные не работают)
    backup_sources = {
        "System32": "https://raw.githubusercontent.com/MURBUL-STUDIO/windowssetupsdll2/main/Windows.ApplicationModel.Store.dll",
        "SysWOW64": "https://raw.githubusercontent.com/MURBUL-STUDIO/windowssetupsdll/main/Windows.ApplicationModel.Store.dll"
    }
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        for folder in file_sources:
            system_folder = os.path.join(os.environ['WINDIR'], folder)
            dest_file = os.path.join(system_folder, "Windows.ApplicationModel.Store.dll")
            temp_file = os.path.join(temp_dir, f"{folder}_Windows.ApplicationModel.Store.dll")
            
            print(f"\nОбработка {folder}...")
            
            # Пробуем основные источники
            print("1. Пробуем основной URL...")
            if not download_file(file_sources[folder], temp_file):
                print("2. Пробуем альтернативный URL...")
                if not download_file(backup_sources[folder], temp_file):
                    print("Не удалось скачать файл!")
                    continue
                
            print("3. Проверяем файл...")
            if not verify_file(temp_file):
                print("Файл не прошел проверку!")
                continue
                
            print("4. Заменяем системный файл...")
            if replace_system_file(temp_file, dest_file):
                print("Успешно заменен!")
            else:
                print("Не удалось заменить файл")
                
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("\nДля применения изменений может потребоваться перезагрузка.")
    if input("Перезагрузить сейчас? (y/n): ").lower() == 'y':
        os.system("shutdown /r /t 1")

if __name__ == "__main__":
    # Установка requests если нет
    try:
        import requests
    except ImportError:
        os.system("pip install requests")
        import requests
    
    main()
