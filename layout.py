def generate_layout(requirements):
    rooms = requirements["rooms"]
    x_cursor = 0
    layout = []

    for room in rooms:
        layout.append({
            "name": room["name"],
            "x": x_cursor,
            "y": 0,
            "w": room["w"],
            "h": room["h"]
        })
        x_cursor += room["w"]
    
    return layout
