import os
import re
from pathlib import Path

def clean_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_length = len(content)
        
        lines = content.split('\n')
        cleaned_lines = []
        in_multiline_string = False
        multiline_char = None
        
        for line in lines:
            stripped = line.lstrip()
            
            if '"""' in line or "'''" in line:
                quote = '"""' if '"""' in line else "'''"
                count = line.count(quote)
                if count == 2 and line.strip().startswith(quote) and line.strip().endswith(quote):
                    continue
                elif count == 1:
                    if not in_multiline_string:
                        in_multiline_string = True
                        multiline_char = quote
                        continue
                    elif multiline_char == quote:
                        in_multiline_string = False
                        multiline_char = None
                        continue
            
            if in_multiline_string:
                continue
            
            if stripped.startswith('#'):
                continue
            
            if '#' in line:
                parts = line.split('#')
                code_part = parts[0]
                
                quote_count_single = code_part.count("'")
                quote_count_double = code_part.count('"')
                
                if quote_count_single % 2 == 0 and quote_count_double % 2 == 0:
                    line = code_part.rstrip()
            
            if line.strip().startswith('print(') and 'debug' in line.lower():
                continue
            
            cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
        
        if len(cleaned_content) < original_length:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            return True, original_length - len(cleaned_content)
        return False, 0
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False, 0

def clean_project(root_path):
    root = Path(root_path)
    total_cleaned = 0
    files_modified = 0
    
    exclude_dirs = {'__pycache__', 'venv', 'node_modules', '.git', 'keys'}
    exclude_files = {'clean_all_comments.py', 'clean_comments_docstrings.py'}
    
    for file_path in root.rglob('*.py'):
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue
        if file_path.name in exclude_files:
            continue
        
        modified, bytes_removed = clean_file(file_path)
        if modified:
            files_modified += 1
            total_cleaned += bytes_removed
            print(f"Limpiado: {file_path.relative_to(root)} (-{bytes_removed} bytes)")
    
    print(f"\n=== Resumen ===")
    print(f"Archivos modificados: {files_modified}")
    print(f"Bytes eliminados: {total_cleaned}")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    print(f"Limpiando proyecto en: {project_root}")
    clean_project(project_root)
