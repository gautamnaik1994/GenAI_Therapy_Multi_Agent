import re
import json


def extract_json_from_message(message_content):
    if not message_content:
        return None
    match = re.search(r'\{[\s\S]*\}', message_content)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception as e:
            print(f"JSON extraction failed: {e}")
            return None
    return None
