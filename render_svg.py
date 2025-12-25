import svgwrite

scale = 20
door_size = 5

def overlap(a, alen, b, blen):
    return max(a,b) < min(a + alen, b + blen)

def rooms_touch(r1, r2):
    sides = []
    #r1 right touches r2 right
    if r1["x"] + r1["w"] == r2["x"] and overlap(r1["y"], r1["h"], r2["y"], r2["h"]):
        sides.append("right")
    #r1 left touches r2 left
    if r2["x"] + r2["w"] == r1["x"] and overlap(r1["y"], r1["h"], r2["y"], r2["h"]):
        sides.append("left")
    #r1 bottom touches r2 top
    if r1["y"] + r1["h"] == r2["y"] and overlap(r1["x"], r1["w"], r2["x"], r2["w"]):
        sides.append("bottom")
    #r1 top touches r2 bottom
    if r2["y"] + r2["h"] == r1["y"] and overlap(r1["x"], r1["w"], r2["x"], r2["w"]):
        sides.append("top")
    return sides

def should_connect(a, b):
    return(
        b["type"] in a.get("connects_to", []) or
        a["type"] in b.get("connects_to", [])
    )

def draw_door(dwg, x, y, w, h, side, color="brown"):
    if side == "right":
        dwg.add(dwg.rect(
            insert=(x + w - 1, y + h / 2 - door_size * scale / 2),
            size=(2, door_size * scale),
            fill=color
        ))
    elif side == "left":
        dwg.add(dwg.rect(
            insert=(x, y + h / 2 - door_size * scale / 2),
            size=(2, door_size * scale),
            fill=color
        ))
    elif side == "bottom":
        dwg.add(dwg.rect(
            insert=(x + w / 2 - door_size * scale / 2, y + h - 1),
            size=(door_size * scale, 2),
            fill=color
        ))
    elif side == "top":
        dwg.add(dwg.rect(
            insert=(x + w / 2 - door_size * scale / 2, y),
            size=(door_size * scale, 2),
            fill=color
        ))
    
def choose_door_side(room, valid_sides, door_perferred=None):
    prefs = door_perferred or room.get("preferred_sides", [])
    for side in prefs:
        if side in valid_sides:
            return side
    return valid_sides[0] if valid_sides else None

def draw_door_px(dwg, x_px, y_px, w_px, h_px, side, center_override_px=None):
    """Draw a door gap on a rectangle given in PIXELS."""
    door_len_px = door_size * scale

    if side == "right":
        cy = center_override_px if center_override_px is not None else (y_px + h_px / 2)
        dwg.add(dwg.rect(
            insert=(x_px + w_px - 1, cy - door_len_px / 2),
            size=(2, door_len_px),
            fill="white",
            stroke="none"
        ))

    elif side == "left":
        cy = center_override_px if center_override_px is not None else (y_px + h_px / 2)
        dwg.add(dwg.rect(
        insert=(x_px, cy - door_len_px / 2),
            size=(2, door_len_px),
            fill="white",
            stroke="none"
        ))

    elif side == "bottom":
        cx = center_override_px if center_override_px is not None else (x_px + w_px / 2)
        dwg.add(dwg.rect(
            insert=(cx - door_len_px / 2, y_px + h_px - 1),
            size=(door_len_px, 2),
            fill="white",
            stroke="none"
        ))

    elif side == "top":
        cx = center_override_px if center_override_px is not None else (x_px + w_px / 2)
        dwg.add(dwg.rect(
            insert=(cx - door_len_px / 2, y_px),
            size=(door_len_px, 2),
            fill="white",
            stroke="none"
        ))


def draw_shared_door(dwg, r1, r2, side):
    """
    Draw ONE door on the shared wall between r1 and r2,
    centered on their overlap segment (in room units).
    """
    x_px = r1["x"] * scale
    y_px = r1["y"] * scale
    w_px = r1["w"] * scale
    h_px = r1["h"] * scale

    if side in ("left", "right"):
        overlap_start = max(r1["y"], r2["y"])
        overlap_end = min(r1["y"] + r1["h"], r2["y"] + r2["h"])
        center_y = ((overlap_start + overlap_end) / 2) * scale  
        draw_door(dwg, x_px, y_px + center_y - (y_px + h_px/2), w_px, h_px, side)

    else:
        overlap_start = max(r1["x"], r2["x"])
        overlap_end = min(r1["x"] + r1["w"], r2["x"] + r2["w"])
        center_x = ((overlap_start + overlap_end) / 2) * scale
        draw_door(dwg, x_px + center_x - (x_px + w_px/2), y_px, w_px, h_px, side)

def pick_side(room, max_x, max_y):
    if room["y"] == 0:
        return "bottom"
    if room["x"] == 0:
        return "left"
    if room["x"] + room["w"] == max_x:
        return "right"
    if room["y"] + room["h"] == max_y:
        return "top"
    return None

def entrance_room(rooms):
    #determine which room is the entrance
    for r in rooms:
        if r.get("is_entrance"):
            return r
    for r in rooms:
        if r["type"] == "dining":
            return r
    return None

def draw_blueprint(rooms, filename):
    #compute building boundaries for rooms later
    max_x = max(room["x"] + room["w"] for room in rooms)
    max_y = max(room["y"] + room["h"] for room in rooms)

    dwg = svgwrite.Drawing(filename, size=(max_x * scale + 10, max_y * scale + 10))

    dwg.add(dwg.rect(
        insert=(0,0),
        size=(max_x * scale, max_y * scale),
        fill="none",
        stroke="black",
        stroke_width=4
    ))

    for room in rooms:
        x = room["x"] * scale
        y = room["y"] * scale
        w = room["w"] * scale
        h = room["h"] * scale

        dwg.add(dwg.rect(
            insert=(x,y),
            size=(w,h),
            fill="lightblue",
            stroke="black",
            stroke_width = 2
        ))

        dwg.add(dwg.text(
            room["name"],
            insert=(x + w / 2, y + h / 2),
            text_anchor = "middle",
            alignment_baseline = "middle",  
            font_size = 14
        ))

    #interior doors
    drawn_pairs = set()  # avoid duplicates
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            a, b = rooms[i], rooms[j]
            if not should_connect(a, b):
                continue  # prevents Bathroom1 <-> Bathroom2 door

            sides = rooms_touch(a, b)
            for side in sides:
                key = (i, j, side)
                if key in drawn_pairs:
                    continue
                draw_shared_door(dwg, a, b, side)
                drawn_pairs.add(key)

    #main exterior entrance
    entry = entrance_room(rooms)
    if entry:
        side = pick_side(entry, max_x, max_y)
        if side:
            draw_door(
                dwg,
                entry["x"] * scale,
                entry["y"] * scale,
                entry["w"] * scale,
                entry["h"] * scale,
                side
            )

    dwg.save()