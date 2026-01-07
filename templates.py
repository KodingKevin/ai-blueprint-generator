def restaurant_template(requirements):
    #use requirements later to scale sizes (seats -> dining area, etc.)
    baths = requirements.get("bathroom", 0)
    has_kitchen = requirements.get("kitchen", 0) > 0

    rooms = []

    rooms.append({
        "name": "Dining",
        "type": "dining",
        "w": 30, "h": 20,
        "is_entrance": True,
        "entrance_side": "top",
        "connects_to": ["kitchen", "bathroom"],
        "preferred_sides": ["right", "bottom", "left", "top"],
    })

    if has_kitchen:
        rooms.append({
            "name": "Kitchen",
            "type": "kitchen",
            "w": 15, "h": 20,
            "connects_to": ["dining"],
            "preferred_sides": ["left", "top", "bottom", "right"],
        })
    
    for i in range(baths):
        rooms.append({
            "name": f"Bathroom {i+1}",
            "type": "bathroom",
            "w": 10, "h": 8,
            "connects_to": ["dining"],
            "preferred_sides": ["top", "left", "right", "bottom"],
        })
    return rooms

def house_template(requirements):
    beds = max(1, requirements.get("bedroom", 2))
    baths = max(1, requirements.get("bathroom", 1))

    rooms = []

    rooms.append({
        "name": "Living",
        "type": "living",
        "w": 24, "h": 18,
        "is_entrance": True,
        "entrance_side": "bottom",   # common “front door” at bottom in your drawings
        "connects_to": ["kitchen", "hall"],
        "preferred_sides": ["right", "top", "left", "bottom"],
    })

    rooms.append({
        "name": "Kitchen",
        "type": "kitchen",
        "w": 16, "h": 12,
        "connects_to": ["living", "dining"],
        "preferred_sides": ["left", "top", "right", "bottom"],
    })

    # Simple hallway to connect private rooms (v1 house needs this or layouts get awkward)
    rooms.append({
        "name": "Hall",
        "type": "hall",
        "w": 6, "h": 18,
        "connects_to": ["living", "bedroom", "bathroom"],
        "preferred_sides": ["top", "right", "left", "bottom"],
    })

    for i in range(beds):
        rooms.append({
            "name" : f"Bedroom {i+1}",
            "type" : "bedroom",
            "w" : 14, "h" : 12,
            "connects_to" : ["hall"],
            "preferred_sides": ["left", "right", "top", "bottom"],
        })

    for i in range(baths):
        rooms.append({
            "name": f"Bathroom {i+1}",
            "type": "bathroom",
            "w": 10, "h": 8,
            "connects_to": ["hall"],
            "preferred_sides": ["top", "left", "right", "bottom"],
        })

    return rooms


def get_template(building_type, requirements):
    t = (building_type or "").lower()
    if "house" in t:
        return house_template(requirements)
    # default
    return restaurant_template(requirements)
