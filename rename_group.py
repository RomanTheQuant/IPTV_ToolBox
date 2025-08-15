import re
import argparse

def update_group_title(file_path, new_group_title):
    # Чтение файла
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Регулярное выражение для поиска строк #EXTINF и их атрибутов
    extinf_pattern = re.compile(r'(#EXTINF:.+?)(group-title=".+?")', re.DOTALL)
    extinf_no_group_pattern = re.compile(r'(#EXTINF:[^\n]+)(?:\n|$)')
    
    # Замена существующего group-title
    new_content = extinf_pattern.sub(fr'\1group-title="{new_group_title}"', content)
    
    # Добавление group-title, если его нет
    new_content = extinf_no_group_pattern.sub(fr'\1 group-title="{new_group_title}"\n', new_content)
    
    # Запись изменений обратно в файл
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update group-title in M3U file')
    parser.add_argument('file', help='Path to the M3U file')
    parser.add_argument('group_title', help='New group-title value')
    
    args = parser.parse_args()
    
    update_group_title(args.file, args.group_title)
    print(f"All channels have been updated with group-title='{args.group_title}'")