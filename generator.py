def parse_text(text):
    text = text.lower()

    spec = {
        "kitchen": 1,
        "bathroom": 1,
        "dining": 1
    }

    if "2 bathroom" in text or "two bathroom" in text:
        spec["bathroom"] = 2
    if "3 bathroom" in text or "three bathroom" in text:
        spec["bathroom"] = 3
    if "0 bathroom" in text or "no bathroom" in text:
        spec["bathroom"] = 0
    return spec

def generate_rooms_from_spec(spec):
    rooms = []

    x_cursor = 0

    #dining room
    dining = {
        "name" : "Dining",
        "x" : 0,
        "y" : 0,
        "w" : 30,
        "h" : 20
    }
    rooms.append(dining)
    x_cursor += dining["w"]

    #kitchen (must be next to dining)
    if spec["kitchen"] > 0:
        kitchen = {
            "name" : "Kitchen",
            "x" : x_cursor,
            "y" : 0,
            "w" : 15,
            "h" : 20
        }
        rooms.append(kitchen)
        x_cursor += kitchen["w"]

    #bathrooms
    for i in range(spec["bathroom"]):
        bathroom = {
            "name" : f"Bathroom {i+1}",
            "x" : i * 10,
            "y" : 20,
            "w" : 10,
            "h" : 8
        }
        rooms.append(bathroom)
    return rooms

def generate_from_text(text):
    spec = parse_text(text)
    return generate_rooms_from_spec(spec)
