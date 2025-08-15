import re
import argparse

def update_group_title(file_path, new_group_title):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#EXTINF:'):
            # Обрабатываем строку #EXTINF
            extinf_line = line.strip()
            channel_name = lines[i+1].strip() if i+1 < len(lines) else ''
            
            # Удаляем старый group-title если есть
            extinf_line = re.sub(r'group-title=".*?"', '', extinf_line)
            extinf_line = re.sub(r'\s+', ' ', extinf_line).strip()
            
            # Добавляем новый group-title перед запятой и названием
            if ',' in extinf_line:
                parts = extinf_line.split(',', 1)
                extinf_line = f'{parts[0]} group-title="{new_group_title}",{parts[1]}'
            else:
                extinf_line = f'{extinf_line} group-title="{new_group_title}"'
            
            new_lines.append(extinf_line + '\n')
            if channel_name:
                new_lines.append(channel_name + '\n')
                i += 1
        else:
            new_lines.append(line)
        i += 1
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update group-title in M3U file')
    parser.add_argument('file', help='Path to the M3U file')
    parser.add_argument('group_title', help='New group-title value')
    
    args = parser.parse_args()
    
    update_group_title(args.file, args.group_title)
    print(f"All channels have been updated with group-title='{args.group_title}'")