def no_overlap(rooms):
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            a = rooms[i]
            b = rooms[j]

            if not (
                a["x"] + a["w"] <= b["x"] or 
                b["x"] + b["w"] <= a["x"] or 
                a["y"] + a["h"] <= b["y"] or
                b["y"] + b["h"] <= a["y"]
            ):
                return False
    return True
