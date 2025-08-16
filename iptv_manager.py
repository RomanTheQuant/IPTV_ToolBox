#!/usr/bin/env python3
import argparse
import re
import sys
from collections import OrderedDict

def parse_m3u_playlist(content):
    """Парсит M3U плейлист и возвращает список каналов с их группами"""
    lines = content.strip().split('\n')
    channels = []
    current_channel = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            # Извлекаем group-title
            group_match = re.search(r'group-title="([^"]*)"', line)
            group_title = group_match.group(1) if group_match else "Без группы"
            
            current_channel = {
                'extinf': line,
                'group': group_title
            }
        elif line.startswith('http') and current_channel:
            current_channel['url'] = line
            channels.append(current_channel)
            current_channel = None
    
    return channels

def group_channels(channels):
    """Группирует каналы по названию группы"""
    groups = OrderedDict()
    for channel in channels:
        group = channel['group']
        if group not in groups:
            groups[group] = []
        groups[group].append(channel)
    return groups

def list_groups(channels):
    """Выводит список всех групп"""
    groups = group_channels(channels)
    print("Список доступных групп:")
    print("-" * 50)
    for i, (group, channel_list) in enumerate(groups.items(), 1):
        print(f"{i:2d}. {group} ({len(channel_list)} каналов)")

def swap_groups(channels, group1, group2):
    """Меняет местами две группы"""
    groups = group_channels(channels)
    
    if group1 not in groups:
        print(f"Ошибка: Группа '{group1}' не найдена")
        return channels
    
    if group2 not in groups:
        print(f"Ошибка: Группа '{group2}' не найдена")
        return channels
    
    # Создаем новый порядок групп
    group_order = list(groups.keys())
    idx1 = group_order.index(group1)
    idx2 = group_order.index(group2)
    
    # Меняем местами
    group_order[idx1], group_order[idx2] = group_order[idx2], group_order[idx1]
    
    # Пересобираем плейлист в новом порядке
    new_channels = []
    for group_name in group_order:
        new_channels.extend(groups[group_name])
    
    print(f"Группы '{group1}' и '{group2}' успешно поменялись местами")
    return new_channels

def remove_groups(channels, groups_to_remove):
    """Удаляет указанные группы"""
    original_count = len(channels)
    groups = group_channels(channels)
    
    # Проверяем существование групп
    not_found = []
    for group in groups_to_remove:
        if group not in groups:
            not_found.append(group)
    
    if not_found:
        print(f"Предупреждение: Следующие группы не найдены: {', '.join(not_found)}")
    
    # Фильтруем каналы
    remaining_groups = [group for group in groups.keys() if group not in groups_to_remove]
    new_channels = []
    removed_count = 0
    
    for group_name in remaining_groups:
        new_channels.extend(groups[group_name])
    
    removed_count = original_count - len(new_channels)
    print(f"Удалено {removed_count} каналов из {len(groups_to_remove) - len(not_found)} групп")
    
    return new_channels

def channels_to_m3u(channels):
    """Преобразует список каналов обратно в M3U формат"""
    result = ["#EXTM3U"]
    for channel in channels:
        result.append(channel['extinf'])
        result.append(channel['url'])
    return '\n'.join(result)

def main():
    parser = argparse.ArgumentParser(
        description='Анализ и модификация IPTV плейлиста по группам',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  %(prog)s playlist.m3u -l                            Показать список групп
  %(prog)s playlist.m3u -s "Спорт" "Фильмы"           Поменять местами группы
  %(prog)s playlist.m3u -r "Новости" "Музыка"         Удалить указанные группы
  %(prog)s playlist.m3u -s "Группа1" "Группа2" -r "Удалить" -o output.m3u
                                                       Комбинированная операция
  %(prog)s playlist.m3u --list --output new.m3u        Альтернативный синтаксис

Важные замечания:
  - Названия групп чувствительны к регистру
  - Если выходной файл не указан, входной файл будет перезаписан
  - При использовании пробелов в названиях групп заключайте их в кавычки
        '''
    )
    
    parser.add_argument('input_file', 
                       help='Входной M3U файл для обработки')
    
    parser.add_argument('-o', '--output', 
                       help='Выходной файл (по умолчанию: перезаписывает входной файл)')
    
    parser.add_argument('-l', '--list', 
                       action='store_true',
                       help='Вывести список всех доступных групп с количеством каналов')
    
    parser.add_argument('-s', '--swap', 
                       nargs=2, 
                       metavar=('ГРУППА1', 'ГРУППА2'),
                       help='Поменять местами две группы. Пример: -s "Спорт" "Фильмы"')
    
    parser.add_argument('-r', '--remove', 
                       nargs='+', 
                       metavar='ГРУППА',
                       help='Удалить одну или несколько групп из плейлиста')
    
    # Добавляем примеры в help
    parser.usage = '%(prog)s input_file [-h] [-l] [-s ГРУППА1 ГРУППА2] [-r ГРУППА [ГРУППА ...]] [-o output_file]'
    
    args = parser.parse_args()
    
    # Проверяем, что хотя бы одна операция указана
    if not any([args.list, args.swap, args.remove]):
        parser.error('Необходимо указать хотя бы одну операцию: -l, -s, или -r. Используйте -h для помощи.')
    
    # Читаем входной файл
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Ошибка: Файл '{args.input_file}' не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)
    
    # Парсим плейлист
    channels = parse_m3u_playlist(content)
    
    if not channels:
        print("Ошибка: Не найдено каналов в плейлисте")
        sys.exit(1)
    
    print(f"Загружено: {len(channels)} каналов")
    
    # Выполняем действия в зависимости от аргументов
    operations_performed = False
    
    if args.list:
        list_groups(channels)
        operations_performed = True
    
    if args.swap:
        channels = swap_groups(channels, args.swap[0], args.swap[1])
        operations_performed = True
    
    if args.remove:
        channels = remove_groups(channels, args.remove)
        operations_performed = True
    
    # Сохраняем результат, если были выполнены модифицирующие операции
    if args.swap or args.remove:
        # Определяем выходной файл
        output_file = args.output if args.output else args.input_file
        
        # Сохраняем результат
        try:
            m3u_content = channels_to_m3u(channels)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(m3u_content)
            print(f"Плейлист успешно сохранен в '{output_file}'")
            print(f"Итого: {len(channels)} каналов")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            sys.exit(1)
    
    if not operations_performed:
        print("Не выполнено ни одной операции")

if __name__ == '__main__':
    main()