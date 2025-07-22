from sentence_transformers import SentenceTransformer
import numpy as np
import re
import difflib
model = SentenceTransformer('DoanKhoi/sbert-phobert-base')


def build_column_embeddings(df, column):
    unique_values = df[column].dropna().unique().tolist()
    embeddings = model.encode(unique_values)
    return unique_values, embeddings

def embedding_map_value(query, unique_values, embeddings):
    query_emb = model.encode([query])[0]
    sims = np.dot(embeddings, query_emb) / (np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_emb))
    best_idx = np.argmax(sims)
    return unique_values[best_idx]


from unidecode import unidecode
from difflib import get_close_matches
def normalize_vn(s):
    return unidecode(s).replace(' ', '').lower()

SPECIAL_LOCATIONS = {
    normalize_vn("Hồ Chí Minh"): "TPHCM",
    normalize_vn("Sài Gòn"): "TPHCM",
    normalize_vn("SàiGòn"): "TPHCM",
}

def fuzzy_match_location(query, unique_names):
    norm_query = normalize_vn(query)
    norm_names = [normalize_vn(name) for name in unique_names]
    matches = get_close_matches(norm_query, norm_names, n=1, cutoff=0.7)
    if matches:
        idx = norm_names.index(matches[0])
        return unique_names[idx]
    return None


def map_location_name(obj_name, df):
    # 1. Embedding lấy ứng viên gần nhất
    unique_obj_names, obj_name_embeddings = build_column_embeddings(df, "OBJ_NAME")
    candidate = embedding_map_value(obj_name, unique_obj_names, obj_name_embeddings)
    norm_candidate = normalize_vn(candidate)
    norm_input = normalize_vn(obj_name)
    # 2. Hậu kiểm: Nếu ứng viên là tên đặc biệt, trả về ánh xạ đặc biệt
    if norm_candidate in SPECIAL_LOCATIONS:
        return SPECIAL_LOCATIONS[norm_candidate]
    # 3. Nếu normalize ứng viên trùng normalize input, giữ nguyên
    if norm_candidate == norm_input:
        return candidate
    # 4. Nếu normalize input nằm trong SPECIAL_LOCATIONS, trả về ánh xạ đặc biệt
    if norm_input in SPECIAL_LOCATIONS:
        return SPECIAL_LOCATIONS[norm_input]
    # 5. Fuzzy matching nếu cần
    fuzzy = fuzzy_match_location(obj_name, unique_obj_names)
    if fuzzy:
        return fuzzy
    # 6. Không thì trả về candidate
    return candidate


def map_column_value(value, df, column):
    """
    Ánh xạ gần đúng giá trị value sang đúng giá trị trong cột column của df.
    """
    values = df[column].dropna().unique()
    matches = difflib.get_close_matches(str(value).lower(), [str(v).lower() for v in values], n=1, cutoff=0.6)
    if matches:
        for v in values:
            if str(v).lower() == matches[0]:
                return v
    return value

def extract_service_name(prompt, df):
    """
    Trích xuất tên dịch vụ từ yêu cầu người dùng và khớp nó với giá trị gần nhất trong cột.
    """
    # Lấy tất cả các tên dịch vụ duy nhất từ dataframe
    service_names = df['SERVICE_NAME'].unique().tolist()
    
    # Check for exact matches first (prioritize longer service names)
    exact_matches = []
    for service in service_names:
        if service.lower() in prompt.lower():
            exact_matches.append((service, len(service)))
    
    if exact_matches:
        exact_matches.sort(key=lambda x: x[1], reverse=True)
        return exact_matches[0][0]
    service_codes = {}
    for service in service_names:
        match = re.search(r'của\s+([A-Z]{3,4})\b', service)
        if match:
            code = match.group(1)
            service_codes[code] = service
    # Tìm các mã trong prompt
    codes_in_prompt = []
    for code in service_codes.keys():
        if code in prompt:
            codes_in_prompt.append((code, service_codes[code]))
    
    if codes_in_prompt:
        # Trả về dịch vụ có mã khớp
        return codes_in_prompt[0][1]
    
    matches = []
    for service in service_names:
        clean_service = service.lower().replace('(', '').replace(')', '')
        clean_words = clean_service.split()
        
        if len(clean_words) >= 2:
            main_phrase = ' '.join(clean_words[:3])
            if main_phrase in prompt.lower():
                matches.append((service, len(main_phrase)))
    
    if matches:
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[0][0]
    
    # Fuzzy matching như cũ
    key_phrases = []
    words = prompt.lower().split()
    for i in range(len(words)-1):
        for j in range(i+1, min(i+4, len(words))):
            key_phrases.append(' '.join(words[i:j+1]))
    
    for phrase in key_phrases:
        if len(phrase.split()) >= 2:
            closest_match = map_column_value(phrase, df, 'SERVICE_NAME')
            if closest_match in service_names:
                return closest_match
    
    return None

def map_sql_values(sql, df, user_request=None):
    """
    Ánh xạ SERVICE_NAME trong SQL sang giá trị gần đúng nhất dựa trên yêu cầu người dùng.
    """
    if user_request and "SERVICE_NAME" in df.columns:
        # Trích xuất tên dịch vụ từ prompt
        extracted_service = extract_service_name(user_request, df)
        
        if extracted_service:
            # Thay thế điều kiện SERVICE_NAME trong truy vấn SQL
            sql = re.sub(
                r"SERVICE_NAME\s*(=|LIKE|IS\s+NOT\s+NULL)\s*'([^']*)'",
                f"SERVICE_NAME = '{extracted_service}'",
                sql,
                flags=re.IGNORECASE
            )
    if "OBJ_NAME" in df.columns:
        # Trường hợp IN với nhiều giá trị
        obj_matches = re.findall(r"OBJ_NAME\s+IN\s*\(([^)]+)\)", sql, re.IGNORECASE)
        if obj_matches:
            locations = [loc.strip("' ") for loc in obj_matches[0].split(",")]
            mapped_locations = [f"'{map_location_name(loc, df)}'" for loc in locations]
            new_obj_clause = f"OBJ_NAME IN ({', '.join(mapped_locations)})"
            sql = re.sub(
                r"OBJ_NAME\s+IN\s*\([^)]+\)",
                new_obj_clause,
                sql,
                flags=re.IGNORECASE
            )
        else:
            # Trường hợp đơn giá trị
            single_match = re.search(r"OBJ_NAME\s*(=|LIKE)\s*'([^']*)'", sql, re.IGNORECASE)
            if single_match:
                location = single_match.group(2)
                mapped_location = map_location_name(location, df)
                sql = re.sub(
                    r"OBJ_NAME\s*(=|LIKE)\s*'([^']*)'", 
                    f"OBJ_NAME = '{mapped_location}'",
                    sql,
                    flags=re.IGNORECASE
                )
    return sql
