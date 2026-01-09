from constraints import no_overlap

def attach(room_to_place, anchor, side):
    """    
    Compute the (x, y) position of `room_to_place` when it is
    attached to the given `anchor` room on a specific side.
    Sides are relative to the anchor room:
        - right: room is placed to the right of anchor
        - left:  room is placed to the left of anchor
        - bottom: room is placed below anchor
        - top:    room is placed above anchor
    """
    if side == "right":
        return anchor["x"] + anchor["w"], anchor["y"]
    if side == "left":
        return anchor["x"] - room_to_place["w"], anchor["y"]
    if side == "bottom":
        return anchor["x"], anchor["y"] + anchor["h"]
    if side == "top":
        return anchor["x"], anchor["y"] - room_to_place["h"]
    raise ValueError("bad side")

def generate_attach_pos(room, anchor, side, step="2"):
    """
    Yield multiple (x,y) candidate placements by attaching room to `anchor`
    on a given side, then SLIDING along the shared wall.
    """
    r_w, r_h = room["w"], room["h"]
    anchor_x, anchor_y, anchor_w, anchor_h = anchor["x"], anchor["y"], anchor["w"], anchor["h"]

    if side == "right":
        x = anchor_x + anchor_w
        #slide y from top to bottom of anchor span
        for y in range(anchor_y - r_h + 1, anchor_y + anchor_h, step):
            yield x, y
    
    elif side == "left":
        x = anchor_x - r_w
        for y in range(anchor_y - r_h + 1, anchor_y + anchor_h, step):
            yield x, y

    elif side == "bottom":
        y = anchor_y + anchor_h
        #slide x across anchor span
        for x in range(anchor_x - r_w + 1, anchor_x + anchor_w, step):
            yield x, y

    elif side == "top":
        y = anchor_y - r_h
        for x in range(anchor_x - r_w + 1, anchor_x + anchor_w, step):
            yield x, y
    
def bbox(rooms):
    """
    Compute the bounding box of a list of rooms.

    Used for:
    - determining overall building size
    - fallback placement
    - normalization to positive coordinates
    """
    min_x = min(r["x"] for r in rooms)
    min_y = min(r["y"] for r in rooms)
    max_x = max(r["x"] + r["w"] for r in rooms)
    max_y = max(r["y"] + r["h"] for r in rooms)
    return min_x, min_y, max_x, max_y

def normalize_to_origin(rooms):
    """
    Shift all rooms so that the minimum x and y coordinates
    are at (0,0).

    This prevents negative coordinates caused by placing rooms
    to the left or above the initial anchor room.

    use to clean the svg
    """
    min_x, min_y, _, _ = bbox(rooms)
    if min_x != 0 or min_y != 0:
        for r in rooms:
            r["x"] -= min_x
            r["y"] -= min_y

def find_anchor_candidates(placed_rooms, room):
    """
    Choose anchors that should connect AND prefer same-zone anchors first.
    Zones reduce "random looking" placements (public stays with public, etc).

    Priority:
    1. Rooms whose type appears in room["connects_to"]
    2. Rooms that want to connect to this room's type
    3. Fallback: ANY placed room (to guarantee placement)
    """
    wants = set(room.get("connects_to", []))
    room_zone = room.get("zone", None)

    same_zone = []
    cross_zone = []

    # anchors are rooms whose type is in wants OR that want to connect to this room type
    for a in placed_rooms:
        connects = (
            a["type"] in wants or
            room["type"] in a.get("connects_to", [])
        )
        if not connects:
            continue

        a_zone = a.get("zone", None)
        if room_zone is not None and a_zone == room_zone:
            same_zone.append(a)
        else:
            cross_zone.append(a)

    if same_zone:
        return same_zone
    if cross_zone:
        return cross_zone
    return placed_rooms

def try_place_adjacent(placed_rooms, room):
    """
    Attempt to place `room` adjacent to one of the already
    placed rooms that it should connect to.

    Placement strategy:
    - Iterate through anchor candidates
    - Try each preferred side (in order)
    - Accept the first placement that causes NO overlap
    """
    anchors = find_anchor_candidates(placed_rooms, room)
    sides = room.get("preferred_sides", ["right", "bottom", "left", "top"])

    for anchor in anchors:
        for side in sides:
            for cx, cy in generate_attach_pos(room, anchor, side, step=2):
                test = dict(room)
                test["x"], test["y"] = cx, cy

                if no_overlap(placed_rooms + [test]):
                    room["x"], room["y"] = cx, cy
                    return True

    return False

def fallback_pack(placed_rooms, room, gap=0):
    """
    Fallback placement method when adjacency placement fails.

    Strategy:
    1. Place room to the right of the current bounding box
    2. If that overlaps, place it below the bounding box
    """
    _, _, max_x, min_y = bbox(placed_rooms)
    room["x"] = max_x + gap
    room["y"] = min_y

    # if overlap anyway, move down by bbox height (rare with this method)
    if not no_overlap(placed_rooms + [room]):
        min_x, min_y, max_x, max_y = bbox(placed_rooms)
        room["x"] = min_x
        room["y"] = max_y + gap

def generate_layout(requirements, template_rooms):
    """
    Main layout generator.

    Inputs:
        requirements   - parsed user input (currently unused here,
                         but reserved for future scaling/logic)
        template_rooms - list of room dicts from templates.py
    """
    # copy & init positions
    rooms = [dict(r) for r in template_rooms]
    for r in rooms:
        r.setdefault("x", 0)
        r.setdefault("y", 0)

    placed = []

    # Place first room at origin
    rooms[0]["x"], rooms[0]["y"] = 0, 0
    placed.append(rooms[0])

    # Place the rest
    for room in rooms[1:]:
        ok = try_place_adjacent(placed, room)
        if not ok:
            fallback_pack(placed, room, gap=0)
        placed.append(room)

    # Ensure everything is in positive coords
    normalize_to_origin(placed)
    return placed