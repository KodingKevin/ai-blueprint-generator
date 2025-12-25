import re

def parse_text(text):
    """
    Parse user input text and return structured requirements.
    Returns:
        dict: {building_type, total_width, kitchen, bathroom, dining}
    """
    text = text.lower()

    spec = {
        "building_type" : "restaurant",
        "total_width": 60,
        "kitchen" : 0,
        "bathroom" : 0,
        "dining" : 1
    }

    #detect kitchen
    if "kitchen" in text:
        spec["kitchen"] = 1

    #detech bathroom
    match = re.search(r'(\d+)\s*bathroom', text)
    if match:
        spec["bathroom"] = int(match.group(1))

    elif "bathroom" in text:
        spec["bathroom"] = 1

    return spec