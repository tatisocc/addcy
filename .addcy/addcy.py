# Archivo: addcy.py
# Ubicación: ~/.addcy/addcy.py

import sys
import os
import re
import unicodedata
import xml.etree.ElementTree as ET

CANONICAL_DICT_PATH = os.path.expanduser("~/.addcy/data.py")

def normalize_word(word):
    if not word: return ""
    word = word.lower()
    normalized = unicodedata.normalize('NFD', word)
    cleaned_word = ''.join(c for c in normalized if unicodedata.category(c).startswith('L') or c == 'ñ')
    return unicodedata.normalize('NFC', cleaned_word).strip()


def extract_words_from_source(file_path):
    absolute_path = os.path.abspath(file_path)
    print(f"-> {absolute_path}")
    source_words = set()
    full_text = ""

    if absolute_path.lower().endswith('.xml'):
        try:
            tree = ET.parse(absolute_path)
            full_text = ' '.join(elem.text for elem in tree.findall('.//*') if elem.text)
        except ET.ParseError:
            print(f"Fallo al parsear XML.")
            return []
    else:
        try:
            with open(absolute_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
        except FileNotFoundError:
            print(f"Archivo '{absolute_path}' no encontrado.")
            return []

    cleaned_text = re.sub(r'[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]', ' ', full_text)
    
    for word in cleaned_text.split():
        normalized = normalize_word(word)
        if normalized and len(normalized) > 0:
            source_words.add(normalized)
                    
    print(f"-> Palabras extraídas de la fuente: {len(source_words)}")
    return list(source_words)


def load_existing_dictionary(dict_path):
    existing_words_normalized = set()
    
    if not os.path.exists(dict_path):
        return []

    try:
        data_variables = {}
        with open(dict_path, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code, {'__file__': dict_path}, data_variables) 

        if 'DATA' in data_variables:
            original_list = data_variables['DATA']
            for word in original_list:
                normalized = normalize_word(word)
                if normalized:
                    existing_words_normalized.add(normalized)

            return list(existing_words_normalized)

        return []
    except Exception as e:
        print(f"Fallo al cargar el diccionario madre: {e}")
        return []


def run_addcy():
    
    if len(sys.argv) < 2:
        print("addcy <ruta_archivo_texto>")
        return

    source_file_path = sys.argv[1]
        
    existing_words = load_existing_dictionary(CANONICAL_DICT_PATH)
    
    new_words = extract_words_from_source(source_file_path)
    
    all_words_set = set(existing_words)
    all_words_set.update(new_words)
    final_list = sorted([w for w in all_words_set if w])
    
    words_added = len(final_list) - len(existing_words)
    
    new_content = [
        f"# Diccionario Canónico Expandido con {os.path.basename(source_file_path)}\n",
        f"# Palabras totales: {len(final_list)}. Palabras añadidas (aproximado): {words_added}.\n\n",
        "DATA = [\n"
    ]
    
    for word in final_list:
        safe_word = word.replace("'", "\\'") 
        new_content.append(f"    '{safe_word}',\n")
            
    new_content.append("]\n")

    try:
        with open(CANONICAL_DICT_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        
        print("Operación Finalizada.")
        print(f"Palabras totales en el diccionario: {len(final_list)}")
        print(f"El archivo data.py ha sido actualizado.")
        
    except IOError:
        print("\nNo se pudo escribir en el archivo data.py.")

if __name__ == "__main__":
    run_addcy()
