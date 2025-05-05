import re

def clean_json_string(json_str):
    return re.sub(r"^```json\s*|\s*```$", "", json_str.strip(), flags=re.DOTALL)
