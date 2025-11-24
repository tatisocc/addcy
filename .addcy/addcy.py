# Archivo: addcy.py
# Ubicación: ~/.addcy/addcy.py

import sys
import os
import re
import unicodedata
import xml.etree.ElementTree as ET

CANONICAL_DICT_PATH = os.path.expanduser("~/.addcy/data.py")

def canonical_hash(word):
    if not word:
        return ""
    word = word.lower()
    return re.sub(r'[^a-záéíóúüñ]', '', word)

def extract_words_from_source(file_path):
    absolute_path = os.path.abspath(file_path)
    source_words_map = {}
    full_text = ""

    if absolute_path.lower().endswith('.xml'):
        try:
            tree = ET.parse(absolute_path)
            full_text = ' '.join(elem.text for elem in tree.findall('.//*') if elem.text)
        except ET.ParseError:
            return {}
    else:
        try:
            with open(absolute_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
        except FileNotFoundError:
            return {}

    cleaned_text = re.sub(r'[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]', ' ', full_text)

    for word_original in cleaned_text.split():
        word_original_lower = word_original.lower()
        key = canonical_hash(word_original_lower)
        if key:
            source_words_map[key] = word_original_lower

    return source_words_map

def load_existing_dictionary(dict_path):
    existing_words_map = {}

    if not os.path.exists(dict_path):
        return {}

    try:
        data_variables = {}
        with open(dict_path, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code, {'__file__': dict_path}, data_variables)

        if 'DATA' in data_variables:
            for word in data_variables['DATA']:
                key = canonical_hash(word)
                if key:
                    existing_words_map[key] = word

        return existing_words_map
    except:
        return {}

def run_addcy():
    if len(sys.argv) < 2:
        return

    source_file_path = sys.argv[1]

    existing_words = load_existing_dictionary(CANONICAL_DICT_PATH)
    new_words = extract_words_from_source(source_file_path)

    all_words = existing_words.copy()
    all_words.update(new_words)

    final_list = sorted(all_words.values())

    new_content = [
        "DATA = [\n"
    ]

    for word in final_list:
        safe_word = word.replace("'", "\\'")
        new_content.append(f"    '{safe_word}',\n")

    new_content.append("]\n")

    try:
        with open(CANONICAL_DICT_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
    except:
        pass

if __name__ == "__main__":
    run_addcy()
