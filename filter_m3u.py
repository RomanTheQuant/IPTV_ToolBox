#!/usr/bin/env python3
import sys
import argparse
import re

def extract_channel_name(extinf_line):
    """Извлекает название канала из строки #EXTINF"""
    # Ищем название канала после последней запятой
    if ',' in extinf_line:
        channel_name = extinf_line.split(',')[-1].strip()
        return channel_name
    return ""

def add_group_title_to_extinf(extinf_line, group_title):
    """Добавляет group-title к строке #EXTINF"""
    # Проверяем, есть ли уже group-title
    if 'group-title=' in extinf_line:
        # Заменяем существующий group-title
        pattern = r'group-title="[^"]*"'
        replacement = f'group-title="{group_title}"'
        return re.sub(pattern, replacement, extinf_line)
    else:
        # Добавляем group-title после #EXTINF:
        # Находим позицию первой запятой
        comma_pos = extinf_line.find(',')
        if comma_pos != -1:
            # Вставляем group-title перед запятой
            return extinf_line[:comma_pos] + f' group-title="{group_title}"' + extinf_line[comma_pos:]
        else:
            # Если запятой нет, добавляем в конец
            return extinf_line.rstrip() + f' group-title="{group_title}"\n'

def filter_m3u_by_extgrp(input_file, output_file, extgrp_name, group_title, sort_channels=True):
    """
    Фильтрует M3U плейлист по заданной группе через #EXTGRP: и сортирует по названию
    
    Args:
        input_file (str): Путь к входному файлу
        output_file (str): Путь к выходному файлу
        extgrp_name (str): Название группы для фильтрации (после #EXTGRP:)
        group_title (str): Название группы для group-title в #EXTINF
        sort_channels (bool): Сортировать каналы по названию
    """
    
    # Читаем входной файл
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Ошибка: Файл {input_file} не найден")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return
    
    # Фильтруем каналы и собираем их в блоки
    channels = []  # Список кортежей (название_канала, [строки_канала])
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Проверяем строку с метаданными канала
        if line.startswith("#EXTINF:"):
            channel_lines = []  # Начинаем собирать блок канала
            channel_name = extract_channel_name(lines[i])  # Извлекаем название
            
            # Добавляем #EXTINF с group-title вместо оригинальной строки
            modified_extinf = add_group_title_to_extinf(lines[i], group_title)
            channel_lines.append(modified_extinf)
            
            # Собираем все строки до следующего канала
            j = i + 1
            found_group = False
            
            while j < len(lines) and not lines[j].strip().startswith("#EXTINF:") and not lines[j].strip().startswith("#EXTM3U"):
                # Пропускаем #EXTGRP: строки и пустые строки
                if lines[j].strip():  # Проверяем, что строка не пустая
                    if lines[j].strip().startswith("#EXTGRP:"):
                        group_value = lines[j].strip()[8:]  # Убираем "#EXTGRP:"
                        if group_value.lower() == extgrp_name.lower():
                            found_group = True
                        # Не добавляем #EXTGRP: в результат
                    else:
                        # Добавляем все остальные строки
                        channel_lines.append(lines[j])
                j += 1
            
            # Если группа найдена, добавляем канал
            if found_group:
                channels.append((channel_name, channel_lines))
            
            i = j
        else:
            i += 1
    
    # Сортируем каналы по названию, если нужно
    if sort_channels:
        channels.sort(key=lambda x: x[0].lower())
    
    # Подготавливаем выходные строки
    output_lines = ["#EXTM3U\n"]  # Добавляем заголовок
    
    # Добавляем отсортированные каналы
    for channel_name, channel_lines in channels:
        output_lines.extend(channel_lines)
        # Добавляем пустую строку между каналами для читаемости
        output_lines.append("\n")
    
    # Убираем последнюю пустую строку, если она есть
    if output_lines and output_lines[-1] == "\n":
        output_lines.pop()
    
    # Записываем отфильтрованный плейлист
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        print(f"Успешно создан файл {output_file} с {len(channels)} каналами")
        print(f"Исходная группа: '{extgrp_name}'")
        print(f"Целевая группа: '{group_title}'")
        if sort_channels:
            print("Каналы отсортированы по названию")
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")

def show_groups(input_file):
    """Показывает все доступные группы в плейлисте"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Ошибка: Файл {input_file} не найден")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return
    
    # Ищем все #EXTGRP: теги
    groups = set()
    lines = content.split('\n')
    
    for line in lines:
        if line.strip().startswith("#EXTGRP:"):
            group_name = line.strip()[8:]  # Убираем "#EXTGRP:"
            groups.add(group_name)
    
    if groups:
        print("Доступные группы:")
        for group in sorted(groups):
            print(f"  - {group}")
    else:
        print("Группы не найдены (убедитесь, что в файле используются теги #EXTGRP:)")

def main():
    parser = argparse.ArgumentParser(description='Фильтрация M3U плейлиста по группе (#EXTGRP:) с сортировкой')
    parser.add_argument('input', nargs='?', help='Входной M3U файл')
    parser.add_argument('output', nargs='?', help='Выходной M3U файл')
    parser.add_argument('extgrp', nargs='?', help='Название группы для фильтрации (после #EXTGRP:)')
    parser.add_argument('group_title', nargs='?', help='Название группы для group-title в #EXTINF')
    parser.add_argument('--list-groups', '-l', action='store_true', help='Показать все доступные группы')
    parser.add_argument('--no-sort', action='store_true', help='Отключить сортировку по названию')
    
    args = parser.parse_args()
    
    # Если запрошена команда показа групп
    if args.list_groups:
        if not args.input:
            print("Ошибка: Укажите входной файл для показа групп")
            return
        show_groups(args.input)
        return
    
    # Проверяем обязательные аргументы
    if not args.input or not args.output or not args.extgrp or not args.group_title:
        parser.print_help()
        return
    
    sort_channels = not args.no_sort
    filter_m3u_by_extgrp(args.input, args.output, args.extgrp, args.group_title, sort_channels)

if __name__ == "__main__":
    main()