import csv
import glob
import os

def merge_csv_files(output_file):
    # Определение текущей рабочей директории
    current_dir = os.getcwd()
    print("Текущая рабочая директория:", current_dir)

    # Полный путь к файлам CSV
    path_to_csv = os.path.join(current_dir, 'domains_list*.csv')

    # Поиск всех CSV файлов с шаблоном 'domains_list*.csv'
    csv_files = glob.glob(path_to_csv)
    print("Найденные файлы CSV:", csv_files)

    if not csv_files:
        print("Файлы CSV не найдены. Проверьте директорию:", current_dir)
        return

    all_domains = set()

    # Чтение и объединение всех уникальных записей из файлов
    for file in csv_files:
        with open(file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Пропускаем заголовок
            for row in reader:
                all_domains.add((row[0].strip(), row[1].strip()))

    # Запись уникальных доменов в новый файл
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['domainName', 'tunnelCode'])
        writer.writerows(all_domains)

    print(f"Файл '{output_file}' успешно создан с уникальными записями.")

# Вызов функции для объединения файлов в один
merge_csv_files('domain_list_all.csv')
