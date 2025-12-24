def generate_layout(requirements):
    """
    Generate room positions based on parsed requirements.
    Each room is a dict: {"name","x","y","w","h"}
    """
    rooms = []

    #dining room
    dining = {"name": "Dining", "x" : 0, "y" : 0, "w" : 30, "h" :  20}
    rooms.append(dining)

    current_x = dining["w"]
    current_y = 0

    #kitchen
    if requirements.get("kitchen", 0) > 0:
        kitchen = {
            "name": "Kitchen", 
            "x" : dining["x"] + dining["w"], 
            "y" : 0, 
            "w": 15, 
            "h" : 20
        }
        rooms.append(kitchen)

    #bathroom
    bath_x = 0
    bath_y = dining["h"]
    for i in range(requirements.get("bathroom", 0)):
        bathroom = {
            "name" : f"Bathroom {i + 1}", 
            "x" : bath_x, 
            "y" : bath_y, 
            "w": 10, 
            "h": 8
        }
        rooms.append(bathroom)
        bath_x += bathroom["w"]
    
    return rooms
