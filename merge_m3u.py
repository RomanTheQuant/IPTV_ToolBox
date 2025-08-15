import argparse

def merge_m3u_playlists(playlist1_path, playlist2_path, output_path):
    """
    Объединяет два M3U плейлиста, добавляя содержимое второго в конец первого.
    
    :param playlist1_path: Путь к первому плейлисту
    :param playlist2_path: Путь ко второму плейлисту
    :param output_path: Путь для сохранения объединенного плейлиста
    """
    try:
        # Читаем содержимое первого плейлиста
        with open(playlist1_path, 'r', encoding='utf-8') as f1:
            playlist1_content = f1.readlines()
        
        # Читаем содержимое второго плейлиста
        with open(playlist2_path, 'r', encoding='utf-8') as f2:
            playlist2_content = f2.readlines()
        
        # Проверяем, является ли файл M3U плейлистом (начинается с #EXTM3U)
        if not playlist1_content[0].startswith('#EXTM3U'):
            print("Предупреждение: Первый файл может не быть M3U плейлистом (отсутствует #EXTM3U в начале)")
        
        if not playlist2_content[0].startswith('#EXTM3U'):
            print("Предупреждение: Второй файл может не быть M3U плейлистом (отсутствует #EXTM3U в начале)")
        
        # Объединяем плейлисты (пропускаем заголовок второго плейлиста если он есть)
        merged_content = playlist1_content
        if playlist2_content[0].startswith('#EXTM3U'):
            merged_content.extend(playlist2_content[1:])
        else:
            merged_content.extend(playlist2_content)
        
        # Записываем объединенный плейлист
        with open(output_path, 'w', encoding='utf-8') as out_file:
            out_file.writelines(merged_content)
        
        print(f"Плейлисты успешно объединены и сохранены в {output_path}")
    
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Объединяет два M3U плейлиста')
    parser.add_argument('playlist1', help='Путь к первому плейлисту')
    parser.add_argument('playlist2', help='Путь ко второму плейлисту')
    parser.add_argument('output', help='Путь для сохранения объединенного плейлиста')
    
    args = parser.parse_args()
    
    merge_m3u_playlists(args.playlist1, args.playlist2, args.output)