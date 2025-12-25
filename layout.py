def generate_layout(requirements):
    """
    Generate room positions based on parsed requirements.
    Each room is a dict: {"name","x","y","w","h"}
    """
    rooms = []

    #dining room
    dining = {
        "name": "Dining", 
        "type": "dining",
        "is_entrance": True,
        "entrance_side": "top",
        "x" : 0, 
        "y" : 0, 
        "w" : 30, 
        "h" :  20,
        "connects_to": ["kitchen", "bathroom"],
        "preferred_sides": ["right", "bottom", "left", "top"]
        }
    rooms.append(dining)

    #kitchen
    if requirements.get("kitchen", 0) > 0:
        kitchen = {
            "name": "Kitchen", 
            "type": "kitchen",
            "x" : dining["x"] + dining["w"], 
            "y" : 0, 
            "w": 15, 
            "h" : 20,
            "connects_to": ["dining"],
            "preferred_sides": ["left", "top", "bottom", "right"]
        }
        rooms.append(kitchen)

    #bathroom
    bath_x = 0
    bath_y = dining["h"]
    for i in range(requirements.get("bathroom", 0)):
        bathroom = {
            "name" : f"Bathroom {i + 1}", 
            "type": "bathroom",
            "x" : bath_x, 
            "y" : bath_y, 
            "w": 10, 
            "h": 8,
            "connects_to": ["dining"],
            "preferred_sides": ["top"]
        }
        rooms.append(bathroom)
        bath_x += bathroom["w"]
    
    return rooms
