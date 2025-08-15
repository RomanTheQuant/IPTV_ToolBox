import re
from collections import defaultdict, OrderedDict

def sort_m3u_playlist(input_file):
    # Чтение файла
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read().splitlines()
    
    # Парсинг плейлиста
    groups = OrderedDict()  # Сохраняет порядок групп
    current_group = None
    current_channel = []
    
    for line in content:
        if line.startswith('#EXTM3U'):
            continue  # Пропускаем заголовок
        
        if line.startswith('#EXTINF'):
            # Извлекаем группу и название канала
            group_match = re.search(r'group-title="([^"]+)"', line)
            if group_match:
                current_group = group_match.group(1)
                if current_group not in groups:
                    groups[current_group] = []
            
            channel_match = re.search(r',([^,]+)$', line)
            if channel_match:
                channel_name = channel_match.group(1).strip()
                current_channel = [line, channel_name]
        elif line and not line.startswith('#'):
            if current_channel and current_group:
                current_channel.append(line)
                groups[current_group].append(current_channel)
                current_channel = []
    
    # Сортировка каналов внутри групп
    for group in groups:
        groups[group].sort(key=lambda x: x[1].lower())  # Сортировка по названию канала
    
    # Сборка отсортированного плейлиста
    output_lines = ['#EXTM3U']
    for group, channels in groups.items():
        for channel_info in channels:
            output_lines.append(channel_info[0])  # EXTINF строка
            output_lines.append(channel_info[2])  # URL
    
    # Запись результата
    output_file = input_file.replace('.txt', '_sorted.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Плейлист успешно отсортирован. Результат сохранен в: {output_file}")

# Запуск
sort_m3u_playlist('online.m3u')