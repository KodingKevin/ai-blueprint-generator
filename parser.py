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
        "dining" : 1,
        "bedroom": 0,
    }

    #detect house
    if "house" in text or "home" in text:
        spec["building_type"] = "house"

    #detect kitchen
    if "kitchen" in text:
        spec["kitchen"] = 1

    #detect bathroom
    match = re.search(r'(\d+)\s*bathroom', text)
    if match:
        spec["bathroom"] = int(match.group(1))

    elif "bathroom" in text:
        spec["bathroom"] = 1

    #detect bedrooms
    match = re.search(r'(\d+)\s*bedroom', text)
    if match:
        spec["bedroom"] = int(match.group(1))
    elif "bedroom" in text:
        spec["bedroom"] = 1
        
    return spec