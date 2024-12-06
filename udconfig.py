import os
import shutil
import stat
import sys
import subprocess

def handle_remove_readonly(func, path, exc_info):
    """
    Убирает атрибут "только чтение" и повторяет удаление.
    """
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def find_folder_fast(folder_name: str, start_path: str = "C:\\") -> str:
    """
    Быстрый поиск папки с указанным именем.
    """
    print(f"Поиск папки: {folder_name}...")
    for entry in os.scandir(start_path):
        if entry.is_dir() and entry.name == folder_name:
            print(f"Папка найдена: {entry.path}")
            return entry.path
    for root, dirs, _ in os.walk(start_path):
        for dir_name in dirs:
            if dir_name == folder_name:
                folder_path = os.path.join(root, dir_name)
                print(f"Папка найдена: {folder_path}")
                return folder_path
    print(f"Папка {folder_name} не найдена.")
    return None

def delete_old_version(old_version_path: str):
    """
    Удаляет папку со старой версией приложения.
    """
    try:
        if old_version_path and os.path.exists(old_version_path):
            print(f"Удаление старой версии: {old_version_path}...")
            shutil.rmtree(old_version_path, onerror=handle_remove_readonly)
            print("Старая версия успешно удалена.")
        else:
            print(f"Старая версия не найдена: {old_version_path}")
    except Exception as e:
        print(f"Ошибка при удалении старой версии: {e}")
        sys.exit(1)

def launch_executable(exe_path: str):
    """
    Запускает указанный исполняемый файл.
    """
    try:
        if os.path.exists(exe_path):
            print(f"Запускаем исполняемый файл: {exe_path}")
            subprocess.Popen([exe_path], shell=True)
        else:
            print(f"Исполняемый файл не найден: {exe_path}")
            sys.exit(1)
    except Exception as e:
        print(f"Ошибка при запуске исполняемого файла: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Название папки старой версии
    old_version_folder = "MWELauncher 2.0v"
    exe_to_launch = r"C:\Users\Asylbek\Desktop\MWE.exe"

    # Быстрый поиск и удаление старой версии
    old_version_path = find_folder_fast(old_version_folder)
    if old_version_path:
        delete_old_version(old_version_path)

    # Запуск новой версии
    launch_executable(exe_to_launch)
