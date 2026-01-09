from constraints import no_overlap
import random

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

def anchor_priority(anchor, room):
    """
    0) same-zone
    1) circulation anchors (hall)
    2) cross-zone
    """
    room_zone = room.get("zone")
    anchor_zone = anchor.get("zone")

    if room_zone is not None and anchor_zone == room_zone:
        return 0
    if anchor_zone == "circulation":
        return 1
    return 2


    #sort by priority
    candidates.sort(key=lambda a: anchor_priority(a, room))
    return candidates

def generate_attach_pos(room, anchor, side, step="2"):
    """
    Yield multiple (x,y) candidate placements by attaching room to `anchor`
    on a given side, then SLIDING along the shared wall.
    """
    r_w, r_h = room["w"], room["h"]
    ax, ay, aw, ah = anchor["x"], anchor["y"], anchor["w"], anchor["h"]

    if side == "right":
        x = ax + aw
        for y in range(ay - r_h + 1, ay + ah, step):
            yield x, y

    elif side == "left":
        x = ax - r_w
        for y in range(ay - r_h + 1, ay + ah, step):
            yield x, y

    elif side == "bottom":
        y = ay + ah
        for x in range(ax - r_w + 1, ax + aw, step):
            yield x, y

    elif side == "top":
        y = ay - r_h
        for x in range(ax - r_w + 1, ax + aw, step):
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
    Find anchors that connect, then sort them by zone priorities.
    """
    wants = set(room.get("connects_to", []))
    candidates = []

    for anchor in placed_rooms:
        connects = (
            anchor["type"] in wants or
            room["type"] in anchor.get("connects_to", [])
        )
        if connects:
            candidates.append(anchor)

    if not candidates:
        candidates = list(placed_rooms)

    candidates.sort(key=lambda a: anchor_priority(a, room))
    return candidates

def try_place_adjacent(placed_rooms, room):
    anchors = find_anchor_candidates(placed_rooms, room)
    sides = room.get("preferred_sides", ["right", "bottom", "left", "top"])

    # Shuffle anchors *within* priority groups (keeps zone preference strong)
    grouped = {0: [], 1: [], 2: []}
    for a in anchors:
        grouped[anchor_priority(a, room)].append(a)
    for k in grouped:
        random.shuffle(grouped[k])
    anchors = grouped[0] + grouped[1] + grouped[2]

    # Keep preferred sides but allow variation
    sides = sides[:]
    if len(sides) > 2 and random.random() < 0.7:
        head = sides[:2]
        tail = sides[2:]
        random.shuffle(tail)
        sides = head + tail
    else:
        random.shuffle(sides)

    for anchor in anchors:
        for side in sides:
            for cx, cy in generate_attach_pos(room, anchor, side, step=2):
                test = dict(room)
                test["x"], test["y"] = cx, cy
                if no_overlap(placed_rooms + [test]):
                    room["x"], room["y"] = cx, cy
                    return True

    return False

def layout_compactness_score(rooms):
    """
    Smaller bounding box = better (more compact).
    """
    min_x = min(r["x"] for r in rooms)
    min_y = min(r["y"] for r in rooms)
    max_x = max(r["x"] + r["w"] for r in rooms)
    max_y = max(r["y"] + r["h"] for r in rooms)
    area = (max_x - min_x) * (max_y - min_y)
    return -area  # bigger negative is worse; closer to 0 is better


def layout_zone_adjacency_score(rooms):
    """
    Reward desirable zone relationships and penalize bad ones.
    v1 approximation: use bounding box touching (shared wall) as adjacency.
    """
    def touches(a, b):
        # axis-aligned rectangle touch check (shared edge overlap)
        # right/left
        if a["x"] + a["w"] == b["x"] or b["x"] + b["w"] == a["x"]:
            return overlap_1d(a["y"], a["h"], b["y"], b["h"])
        # top/bottom
        if a["y"] + a["h"] == b["y"] or b["y"] + b["h"] == a["y"]:
            return overlap_1d(a["x"], a["w"], b["x"], b["w"])
        return False

    def overlap_1d(a, alen, b, blen):
        return max(a, b) < min(a + alen, b + blen)

    score = 0
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            a, b = rooms[i], rooms[j]
            if not touches(a, b):
                continue

            az, bz = a.get("zone"), b.get("zone")

            # Good: private next to circulation (bedrooms/baths off hall)
            if (az == "private" and bz == "circulation") or (bz == "private" and az == "circulation"):
                score += 25

            # Good: public next to service (kitchen near living/dining)
            if (az == "public" and bz == "service") or (bz == "public" and az == "service"):
                score += 12

            # Bad: private directly touching service (bedroom touching kitchen)
            if (az == "private" and bz == "service") or (bz == "private" and az == "service"):
                score -= 20

    return score


def score_layout(rooms):
    """
    Total score: higher is better.
    """
    return (
        layout_zone_adjacency_score(rooms)
        + layout_compactness_score(rooms)
    )

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

def generate_layout(requirements, template_rooms, attempts=20):
    best_rooms = None
    best_score = None

    for _ in range(attempts):
        rooms = [dict(r) for r in template_rooms]
        for r in rooms:
            r.setdefault("x", 0)
            r.setdefault("y", 0)

        placed = []
        rooms[0]["x"], rooms[0]["y"] = 0, 0
        placed.append(rooms[0])

        for room in rooms[1:]:
            ok = try_place_adjacent(placed, room)
            if not ok:
                fallback_pack(placed, room, gap=0)
            placed.append(room)

        normalize_to_origin(placed)

        s = score_layout(placed)
        if best_score is None or s > best_score:
            best_score = s
            best_rooms = placed

    return best_rooms