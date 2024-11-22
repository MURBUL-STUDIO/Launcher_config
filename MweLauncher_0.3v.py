import os
import requests
import sys
import subprocess

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
            print("Файл UPDATE.txt не найден в репозитории.")
            return False
        elif update_content.strip():  # Если файл существует и не пуст
            print("Файл UPDATE.txt найден в репозитории.")
            return True
        else:  # Если файл пустой
            print("Файл UPDATE.txt существует, но он пустой.")
            return False
    except Exception as e:
        print(f"Ошибка при проверке файла UPDATE.txt: {e}")
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

def update_application(owner: str, repo: str, branch: str, file_path: str, local_folder: str):
    """Обновляет приложение: скачивает новый файл и запускает его."""
    try:
        print("Начинаем обновление...")
        parent_folder = os.path.dirname(local_folder)
        temp_folder = os.path.join(parent_folder, "MWELauncher3.0v")

        # Скачиваем файл
        downloaded_file = download_file(owner, repo, branch, file_path, temp_folder)

        # Запускаем обновленный код с флагом "skip_update_check"
        print(f"Запускаем {downloaded_file} для завершения обновления...")
        subprocess.Popen(["python", downloaded_file, "--skip-update-check"])

        # Завершаем текущий процесс
        print("Обновление завершено. Выход из текущей программы.")
        sys.exit()

    except Exception as e:
        print(f"Ошибка при обновлении: {e}")
        sys.exit(1)

# Параметры для обновления
local_folder = r"C:\Users\Asylbek\Desktop\MWELauncher 3.0v"
owner = "MURBUL-STUDIO"
repo = "m4bfsuehsbrshwglsgkjrghsrh4r2e44"
update_file_path = "UPDATE.txt"
branch = "main"
testfile_path = "MweLauncher_0.3v.py"

# Проверяем аргументы командной строки
skip_update_check = "--skip-update-check" in sys.argv

if not skip_update_check:
    print("Запуск программы...")
    has_update = check_update_file_remote(owner, repo, update_file_path, branch)

    if has_update:
        print("Обновление доступно. Начинаем процесс обновления.")
        update_application(owner, repo, branch, testfile_path, local_folder)
    else:
        print("Обновлений не найдено. Переход к меню.")
else:
    print("Пропуск проверки обновлений (запущено с флагом --skip-update-check).")

# Цикл с действиями
while True:
    print("\nМеню:")
    print("2. Действие 2")
    print("3. Действие 3")
    print("4. Действие 4")
    print("5. Действие 5")
    print("Чтобы выйти, введите: exit")
    action = input("Выберите действие: ")

    if action == "2":
        print("Выполняется действие 2")

    elif action == "3":
        print("Выполняется действие 3")

    elif action == "4":
        print("Выполняется действие 4")

    elif action == "5":
        print("Выполняется действие 5")

    elif action == "exit":
        sys.exit()

    else:
        print("Ошибка: неверное действие")
