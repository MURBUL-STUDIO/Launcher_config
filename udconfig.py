import os
import shutil
import stat
import sys

def handle_remove_readonly(func, path, exc_info):
    """
    Убирает атрибут "только чтение" и повторяет удаление.
    """
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def find_folder(folder_name: str, start_path: str = "C:\\") -> str:
    """
    Ищет папку с указанным именем на всём компьютере, начиная с указанного пути.
    """
    print(f"Ищем папку {folder_name} во всех директориях...")
    for root, dirs, _ in os.walk(start_path):
        if folder_name in dirs:
            folder_path = os.path.join(root, folder_name)
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

def launch_new_version(new_version_path: str):
    """
    Запускает приложение из новой версии.
    """
    try:
        main_script_path = os.path.join(new_version_path, "main.py")
        if os.path.exists(main_script_path):
            print(f"Запускаем новую версию: {main_script_path}")
            os.system(f"python \"{main_script_path}\"")
        else:
            print(f"Основной файл новой версии не найден: {main_script_path}")
            sys.exit(1)
    except Exception as e:
        print(f"Ошибка при запуске новой версии: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Названия папок старой и новой версий
    old_version_folder = "MWELauncher 2.0v"
    new_version_folder = "MWELauncher 3.0v"

    # Путь новой версии (из текущего рабочего каталога)
    current_folder = os.path.dirname(os.path.abspath(__file__))
    new_version_path = os.path.join(current_folder)

    # Поиск старой версии
    old_version_path = find_folder(old_version_folder)

    # Удаляем старую версию
    delete_old_version(old_version_path)

    # Запускаем новую версию
    launch_new_version(new_version_path)
