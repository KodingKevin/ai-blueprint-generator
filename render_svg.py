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

def draw_door(dwg, x, y, w, h, side, center_override=None):
    #all in pixels
    door_len = door_size * scale
    if side == "right":
        center_y = center_override if center_override is not None else(y + h / 2)
        dwg.add(dwg.rect(
            insert=(x + w - 1, center_y - door_len / 2),
            size=(2, door_len),
            fill="white",
            stroke="none"
        ))
    elif side == "left":
        center_y = center_override if center_override is not None else(y + h / 2)
        dwg.add(dwg.rect(
            insert=(x, center_y / 2),
            size=(2, door_len),
            fill="white",
            stroke="none"
        ))
    elif side == "bottom":
        center_x = center_override if center_override is not None else(x + w / 2)
        dwg.add(dwg.rect(
            insert=(center_x - door_len / 2, y + h - 1),
            size=(door_len, 2),
            fill="white",
            stroke="none"
        ))
    elif side == "top":
        center_x = center_override if center_override is not None else(x + w / 2)
        dwg.add(dwg.rect(
            insert=(center_x - door_len / 2, y),
            size=(door_len, 2),
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

    if side in ("top", "bottom"):
        overlap_start = max(r1["x"], r2["x"])
        overlap_end = min(r1["x"] + r1["w"], r2["x"] + r2["w"])
        center_x_units = (overlap_start + overlap_end) / 2
        center_x_px = center_x_units * scale
        draw_door(dwg, x_px, y_px, w_px, h_px, side, center_override=center_x_px)

    if side in ("left", "right"):
        overlap_start = max(r1["y"], r2["y"])
        overlap_end = min(r1["y"] + r1["h"], r2["y"] + r2["h"])
        center_y_units = (overlap_start + overlap_end) / 2
        center_y_px = center_y_units * scale
        draw_door(dwg, x_px, y_px, w_px, h_px, side, center_override=center_y_px)

def exterior_side(room, max_x, max_y):
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
    return max(rooms, key=lambda r: r["w"] * r["h"])

def pick_entrance_side(room, max_x, max_y):
    outside = exterior_side(room, max_x, max_y)
    if not outside:
        return None

    preferred = room.get("entrance_side")
    if preferred in outside:
        return preferred

    # fallback preference order
    for s in ["bottom", "left", "right", "top"]:
        if s in outside:
            return s
    return outside[0]

def draw_blueprint(rooms, filename):
    #compute building boundaries for rooms later
    max_x = max(room["x"] + room["w"] for room in rooms)
    max_y = max(room["y"] + room["h"] for room in rooms)

    dwg = svgwrite.Drawing(filename, size=(max_x * scale + 10, max_y * scale + 10))

    #outer wall
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
                continue
            for side in rooms_touch(a, b):
                draw_shared_door(dwg, a, b, side)

    #main exterior entrance
    entry = entrance_room(rooms)
    side = exterior_side(entry, max_x, max_y)
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