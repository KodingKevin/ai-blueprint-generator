import svgwrite

scale = 20
door_size = 5          # door length in "room units"
wall_thickness = 4     # px (matches outer wall stroke width)
margin = 12            # px margin so exterior doors never get clipped

def overlap(a, alen, b, blen):
    return max(a, b) < min(a + alen, b + blen)


def rooms_touch(r1, r2):
    """
    Returns a list of sides (relative to r1) where r1 touches r2:
    "right", "left", "bottom", "top"
    """
    sides = []
    # r1 right touches r2 left
    if r1["x"] + r1["w"] == r2["x"] and overlap(r1["y"], r1["h"], r2["y"], r2["h"]):
        sides.append("right")
    # r1 left touches r2 right
    if r2["x"] + r2["w"] == r1["x"] and overlap(r1["y"], r1["h"], r2["y"], r2["h"]):
        sides.append("left")
    # r1 bottom touches r2 top
    if r1["y"] + r1["h"] == r2["y"] and overlap(r1["x"], r1["w"], r2["x"], r2["w"]):
        sides.append("bottom")
    # r1 top touches r2 bottom
    if r2["y"] + r2["h"] == r1["y"] and overlap(r1["x"], r1["w"], r2["x"], r2["w"]):
        sides.append("top")
    return sides


def should_connect(a, b):
    return (
        b["type"] in a.get("connects_to", []) or
        a["type"] in b.get("connects_to", [])
    )


def draw_door(dwg, x, y, w, h, side, center_override=None):
    """
    Draw a simple rectangular 'gap' door on a room wall.
    x,y,w,h are in pixels for the room rect.
    side is one of: left/right/top/bottom
    center_override is the CENTER coordinate in pixels along the wall axis.
    """
    door_len = door_size * scale

    if side == "right":
        center_y = center_override if center_override is not None else (y + h / 2)
        dwg.add(dwg.rect(
            insert=(x + w - 1, center_y - door_len / 2),
            size=(2, door_len),
            fill="white",
            stroke="none"
        ))

    elif side == "left":
        center_y = center_override if center_override is not None else (y + h / 2)
        dwg.add(dwg.rect(
            insert=(x, center_y - door_len / 2),
            size=(2, door_len),
            fill="white",
            stroke="none"
        ))

    elif side == "bottom":
        center_x = center_override if center_override is not None else (x + w / 2)
        dwg.add(dwg.rect(
            insert=(center_x - door_len / 2, y + h - 1),
            size=(door_len, 2),
            fill="white",
            stroke="none"
        ))

    elif side == "top":
        center_x = center_override if center_override is not None else (x + w / 2)
        dwg.add(dwg.rect(
            insert=(center_x - door_len / 2, y),
            size=(door_len, 2),
            fill="white",
            stroke="none"
        ))

def door_opening_on_shared_wall(r1, r2, side):
    """
    Return a door opening segment on the shared wall in ROOM UNITS.
    Output format:
      ("v", x, y1, y2) for vertical opening at x from y1..y2
      ("h", y, x1, x2) for horizontal opening at y from x1..x2
    Returns None if overlap too small.
    """
    min_overlap_units = door_size + 2

    if side in ("left", "right"):
        overlap_start = max(r1["y"], r2["y"])
        overlap_end = min(r1["y"] + r1["h"], r2["y"] + r2["h"])
        if overlap_end - overlap_start < min_overlap_units:
            return None

        center = (overlap_start + overlap_end) / 2
        y1 = center - door_size / 2
        y2 = center + door_size / 2

        # x coordinate of the shared wall (in units)
        x = r1["x"] if side == "left" else (r1["x"] + r1["w"])
        return ("v", x, y1, y2)

    if side in ("top", "bottom"):
        overlap_start = max(r1["x"], r2["x"])
        overlap_end = min(r1["x"] + r1["w"], r2["x"] + r2["w"])
        if overlap_end - overlap_start < min_overlap_units:
            return None

        center = (overlap_start + overlap_end) / 2
        x1 = center - door_size / 2
        x2 = center + door_size / 2

        # y coordinate of the shared wall (in units)
        y = r1["y"] if side == "top" else (r1["y"] + r1["h"])
        return ("h", y, x1, x2)

    return None

def draw_shared_door(dwg, r1, r2, side, offset_x_px=0, offset_y_px=0):
    """
    Draw ONE door on the shared wall between r1 and r2,
    centered on their overlap segment (in room units).
    offset_x_px / offset_y_px lets us shift drawing by a margin.
    """
    x_px = r1["x"] * scale + offset_x_px
    y_px = r1["y"] * scale + offset_y_px
    w_px = r1["w"] * scale
    h_px = r1["h"] * scale
    min_overlap_units = door_size + 2

    if side in ("top", "bottom"):
        overlap_start = max(r1["x"], r2["x"])
        overlap_end = min(r1["x"] + r1["w"], r2["x"] + r2["w"])
        overlap_len = overlap_end - overlap_start
        if overlap_len < min_overlap_units:
            return
        center_x_units = (overlap_start + overlap_end) / 2
        center_x_px = center_x_units * scale + offset_x_px
        draw_door(dwg, x_px, y_px, w_px, h_px, side, center_override=center_x_px)

    elif side in ("left", "right"):
        overlap_start = max(r1["y"], r2["y"])
        overlap_end = min(r1["y"] + r1["h"], r2["y"] + r2["h"])
        overlap_len = overlap_end - overlap_start
        if overlap_len < min_overlap_units:
            return
        center_y_units = (overlap_start + overlap_end) / 2
        center_y_px = center_y_units * scale + offset_y_px
        draw_door(dwg, x_px, y_px, w_px, h_px, side, center_override=center_y_px)


def exterior_sides(room, max_x, max_y):
    """
    SVG coords: (0,0) is TOP-left.
    So:
      y == 0 is top edge
      y+h == max_y is bottom edge
    """
    sides = []
    if room["y"] == 0:
        sides.append("top")
    if room["x"] == 0:
        sides.append("left")
    if room["x"] + room["w"] == max_x:
        sides.append("right")
    if room["y"] + room["h"] == max_y:
        sides.append("bottom")
    return sides


def entrance_room(rooms):
    for r in rooms:
        if r.get("is_entrance"):
            return r
    for r in rooms:
        if r["type"] == "dining":
            return r
    return max(rooms, key=lambda r: r["w"] * r["h"])


def pick_entrance_side(room, max_x, max_y):
    outside = exterior_sides(room, max_x, max_y)
    if not outside:
        return None

    preferred = room.get("entrance_side")
    if preferred in outside:
        return preferred

    for s in ["bottom", "left", "right", "top"]:
        if s in outside:
            return s

    return outside[0]

def choose_best_shared_side(a, b, touching_sides):
    """
    touching_sides are sides relative to 'a' (output of rooms_touch(a,b)).
    We rank sides using a['preferred_sides'] and b['preferred_sides'].

    """
    def flip(side):
        return {"left":"right", "right":"left", "top":"bottom", "bottom":"top"}[side]

    a_pref = a.get("preferred_sides", [])
    b_pref = b.get("preferred_sides", [])

    # Lower score is better
    def score(side_for_a):
        side_for_b = flip(side_for_a)

        # If a doesn't specify prefs, treat as neutral
        a_rank = a_pref.index(side_for_a) if side_for_a in a_pref else 999

        # If b doesn't specify prefs, treat as neutral
        b_rank = b_pref.index(side_for_b) if side_for_b in b_pref else 999

        # Weighted sum: prioritize a slightly, but both matter
        return a_rank * 10 + b_rank

    return min(touching_sides, key=score)

def draw_exterior_door(dwg, x, y, w, h, side):
    """
    Push door slightly outward so the outer wall stroke doesn't cover it.
    """
    offset = wall_thickness / 2
    if side == "top":
        draw_door(dwg, x, y - offset, w, h, side)
    elif side == "bottom":
        draw_door(dwg, x, y + offset, w, h, side)
    elif side == "left":
        draw_door(dwg, x - offset, y, w, h, side)
    elif side == "right":
        draw_door(dwg, x + offset, y, w, h, side)

def room_edges(room):
    """Return the 4 edges of a room in ROOM UNITS."""
    x, y, w, h = room["x"], room["y"], room["w"], room["h"]
    # each edge: ((x1,y1),(x2,y2)) in units
    return [
        ((x, y), (x + w, y)),         # top
        ((x, y + h), (x + w, y + h)), # bottom
        ((x, y), (x, y + h)),         # left
        ((x + w, y), (x + w, y + h)), # right
    ]

def norm_edge(e):
    """Normalize edge direction so shared walls match."""
    (a, b) = e
    return (a, b) if a <= b else (b, a)

def draw_walls(dwg, rooms, offset_x_px, offset_y_px, openings=None):
    """
    Draw walls ONCE using shared-edge counting.
    If openings provided, cut gaps (doors) into wall lines.
    openings: list of ("v", x, y1, y2) or ("h", y, x1, x2) in ROOM UNITS.
    """
    openings = openings or []

    # index openings for quick lookup
    v_open = {}  # x -> list of (y1,y2)
    h_open = {}  # y -> list of (x1,x2)

    for o in openings:
        if o[0] == "v":
            _, x, y1, y2 = o
            v_open.setdefault(x, []).append((y1, y2))
        else:
            _, y, x1, x2 = o
            h_open.setdefault(y, []).append((x1, x2))

    edge_counts = {}
    for r in rooms:
        for e in room_edges(r):
            k = norm_edge(e)
            edge_counts[k] = edge_counts.get(k, 0) + 1

    for (p1, p2), count in edge_counts.items():
        (x1u, y1u), (x2u, y2u) = p1, p2

        stroke_w = wall_thickness if count == 1 else 2

        # vertical edge
        if x1u == x2u:
            x = x1u
            y1, y2 = sorted([y1u, y2u])

            cuts = v_open.get(x, [])
            cuts = [(max(y1, c1), min(y2, c2)) for (c1, c2) in cuts]
            cuts = [(c1, c2) for (c1, c2) in cuts if c2 > c1]
            cuts.sort()

            segments = []
            cursor = y1
            for c1, c2 in cuts:
                if c1 > cursor:
                    segments.append((cursor, c1))
                cursor = max(cursor, c2)
            if cursor < y2:
                segments.append((cursor, y2))

            for sy1, sy2 in segments:
                dwg.add(dwg.line(
                    start=(x * scale + offset_x_px, sy1 * scale + offset_y_px),
                    end=(x * scale + offset_x_px, sy2 * scale + offset_y_px),
                    stroke="black",
                    stroke_width=stroke_w
                ))

        # horizontal edge
        else:
            y = y1u
            x1, x2 = sorted([x1u, x2u])

            cuts = h_open.get(y, [])
            cuts = [(max(x1, c1), min(x2, c2)) for (c1, c2) in cuts]
            cuts = [(c1, c2) for (c1, c2) in cuts if c2 > c1]
            cuts.sort()

            segments = []
            cursor = x1
            for c1, c2 in cuts:
                if c1 > cursor:
                    segments.append((cursor, c1))
                cursor = max(cursor, c2)
            if cursor < x2:
                segments.append((cursor, x2))

            for sx1, sx2 in segments:
                dwg.add(dwg.line(
                    start=(sx1 * scale + offset_x_px, y * scale + offset_y_px),
                    end=(sx2 * scale + offset_x_px, y * scale + offset_y_px),
                    stroke="black",
                    stroke_width=stroke_w
                ))

def draw_blueprint(rooms, filename):
    # compute building bounds in ROOM UNITS
    max_x = max(room["x"] + room["w"] for room in rooms)
    max_y = max(room["y"] + room["h"] for room in rooms)

    width_px = max_x * scale
    height_px = max_y * scale

    # Add margins so exterior doors never get clipped
    dwg = svgwrite.Drawing(
        filename,
        size=(width_px + 2 * margin, height_px + 2 * margin)
    )

    # Rooms
    for room in rooms:
        x = room["x"] * scale + margin
        y = room["y"] * scale + margin
        w = room["w"] * scale
        h = room["h"] * scale

        dwg.add(dwg.rect(
            insert=(x, y),
            size=(w, h),
            fill="lightblue",
            stroke="none",
        ))

        dwg.add(dwg.text(
            room["name"],
            insert=(x + w / 2, y + h / 2),
            text_anchor="middle",
            alignment_baseline="middle",
            font_size=14
        ))
    openings = []
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            a, b = rooms[i], rooms[j]
            if not should_connect(a, b):
                continue
            sides = rooms_touch(a, b)
            if not sides:
                continue

            best_side = choose_best_shared_side(a, b, sides)
            o = door_opening_on_shared_wall(a, b, best_side)
            if o:
                openings.append(o)

    draw_walls(dwg, rooms, margin, margin, openings=openings)
    
    # Exterior entrance
    entry = entrance_room(rooms)
    side = pick_entrance_side(entry, max_x, max_y)
    if side:
        draw_exterior_door(
            dwg,
            entry["x"] * scale + margin,
            entry["y"] * scale + margin,
            entry["w"] * scale,
            entry["h"] * scale,
            side
        )

    dwg.save()
