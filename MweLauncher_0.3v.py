import os
import requests
import sys
import subprocess
import zipfile
import shutil
import winreg

def get_remote_file_content(owner: str, repo: str, file_path: str, branch: str = "main") -> str:
    """Получает содержимое файла с GitHub."""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    elif response.status_code == 404:
        return None  # Файл не найден
    else:
        raise Exception(f"Не удалось получить файл: {response.status_code}")

def check_update_file_remote(owner: str, repo: str, file_path: str, branch: str = "main") -> bool:
    """Проверяет наличие файла UPDATE.txt на GitHub."""
    try:
        update_content = get_remote_file_content(owner, repo, file_path, branch)
        if update_content is None:  # Если файл отсутствует
            print("Обновлений нет.")
            return False
        elif update_content.strip():  # Если файл существует и не пуст
            print("Загрузка обновлений...")
            return True
        else:  # Если файл пустой
            print("CODE_ERROR: Файл UPDATE.txt существует, но он пустой.")
            return False
    except Exception as e:
        print(f"Ошибка при проверке файла UPDATE: {e}")
        return False

def download_file(owner: str, repo: str, branch: str, file_path: str, destination: str):
    """Скачивает указанный файл с GitHub и сохраняет его локально."""
    try:
        file_content = get_remote_file_content(owner, repo, file_path, branch)
        if file_content is None:
            raise FileNotFoundError(f"Ошибка: Файл {file_path} отсутствует в репозитории.")
        os.makedirs(destination, exist_ok=True)
        local_file_path = os.path.join(destination, os.path.basename(file_path))
        with open(local_file_path, "w", encoding="utf-8") as file:
            file.write(file_content)
        print(f"Файл {file_path} успешно скачан в {local_file_path}.")
        return local_file_path
    except FileNotFoundError as e:
        print(e)
        raise
    except Exception as e:
        raise Exception(f"Ошибка при скачивании файла {file_path}: {e}")

def download_and_extract_zip(url: str, extract_to: str):
    """Скачивает ZIP-архив и разархивирует его."""
    zip_path = os.path.join(extract_to, "x64.zip")
    download_file_from_url(url, zip_path)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Архив разархивирован в {extract_to}")
    except Exception as e:
        print(f"Ошибка при разархивировании архива: {e}")
        sys.exit(1)

def download_file_from_url(url: str, destination: str):
    """Скачивает файл по URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки при скачивании
        with open(destination, 'wb') as file:
            file.write(response.content)
        print(f"Файл скачан: {destination}")
    except Exception as e:
        print(f"Ошибка при скачивании файла: {e}")
        sys.exit(1)

def replace_system_files(extracted_folder: str):
    """Заменяет файлы Windows.ApplicationModel.Store.dll в системных папках."""
    try:
        # Пути к папкам System32 и SysWOW64
        system32_path = r"C:\Windows\System32"
        syswow64_path = r"C:\Windows\SysWOW64"
        
        # Пути к новым файлам
        dll_file_name = "Windows.ApplicationModel.Store.dll"
        extracted_system32_path = os.path.join(extracted_folder, "System32", dll_file_name)
        extracted_syswow64_path = os.path.join(extracted_folder, "SysWOW64", dll_file_name)

        # Заменяем файлы в папках System32 и SysWOW64
        if os.path.exists(extracted_system32_path):
            shutil.copy(extracted_system32_path, os.path.join(system32_path, dll_file_name))
            print(f"Заменен файл в {system32_path}")

        if os.path.exists(extracted_syswow64_path):
            shutil.copy(extracted_syswow64_path, os.path.join(syswow64_path, dll_file_name))
            print(f"Заменен файл в {syswow64_path}")

    except Exception as e:
        print(f"Ошибка при замене файлов: {e}")
        sys.exit(1)

def add_to_startup(file_path: str):
    """Добавляет программу в автозагрузку Windows."""
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "MWE.exe"

        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as registry_key:
            winreg.SetValueEx(registry_key, app_name, 0, winreg.REG_SZ, file_path)
        print(f"Программа добавлена в автозагрузку: {file_path}")
    except Exception as e:
        print(f"Ошибка при добавлении в автозагрузку: {e}")

def remove_from_startup():
    """Удаляет программу из автозагрузки Windows."""
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "MWE.exe"

        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as registry_key:
            winreg.DeleteValue(registry_key, app_name)
        print("Программа удалена из автозагрузки.")
    except FileNotFoundError:
        print("Программа не найдена в автозагрузке.")
    except Exception as e:
        print(f"Ошибка при удалении из автозагрузки: {e}")

# Параметры для обновления
local_folder = r"C:\Users\Asylbek\Desktop\MWELauncher 3.0v"
owner = "MURBUL-STUDIO"
repo = "Launcher_config"
update_file_path = "UPDATE.txt"
branch = "main"
testfile_path = "MweLauncher_0.3v.py"

# Проверка наличия обновлений
print("Запуск программы...")
has_update = check_update_file_remote(owner, repo, update_file_path, branch)

if has_update:
    print("Обновление доступно. Скачиваем...")
    update_application(owner, repo, branch, testfile_path, local_folder)
else:
    print("Обновлений не найдено.")

# Цикл с действиями
exe_path = r"C:\Users\Asylbek\Desktop\MWE.exe"

while True:
    print("\nМеню:")
    print("1. Download Minecraft Windows Edition")
    print("2. Settings")
    print("3. About Us")
    print("Чтобы выйти, введите: exit")
    action = input("Выберите действие: ")

    if action == "1":
        print("Скачиваем и разархивируем архив Minecraft Windows Edition...")
        # Скачиваем и разархивируем архив
        download_and_extract_zip("https://example.com/x64.rar", r"C:\Users\Asylbek\Desktop\x64")
        # Заменяем файлы в системе
        replace_system_files(r"C:\Users\Asylbek\Desktop\x64")
        print("Файлы заменены.")

    elif action == "2":
        print("""Settings:
        Run MWE Launcher when Windows starts: mwe-runwin / for OFF: mwe-stopwin.
        """)
        sub_action = input("Введите команду: ")
        if sub_action == "mwe-runwin":
            add_to_startup(exe_path)
        elif sub_action == "mwe-stopwin":
            remove_from_startup()
        else:
            print("Ошибка: Неверная команда.")

    elif action == "3":
        print("""About Us:  
        Created by: MURBUL   
        Version: 0.3-alpha
        """)

    elif action == "mwe-runwin":
        add_to_startup(exe_path)

    elif action == "mwe-stopwin":
        remove_from_startup()

    elif action == "exit":
        sys.exit()

    else:
        print("Ошибка-1: Неверное действие")