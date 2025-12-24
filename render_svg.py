import svgwrite

scale = 20
door_size = 5

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

    def overlap(a, alen, b, blen):
        return max(a,b) < min(a + alen, b + blen)

    def rooms_touch(r1, r2):
        #right-left
        if r1["x"] + r1["w"] == r2["x"] and overlap(r1["y"], r1["h"], r2["y"], r2["h"]):
            return "right"
        if r2["x"] + r2["w"] == r1["x"] and overlap(r1["y"], r1["h"], r2["y"], r2["h"]):
            return "left"
        
        #top-bot
        if r1["y"] + r1["h"] == r2["y"] and overlap(r1["x"], r1["w"], r2["x"], r2["w"]):
            return "bottom"
        if r2["y"] + r2["h"] == r1["y"] and overlap(r1["x"], r1["w"], r2["x"], r2["w"]):
            return "top"
        return None

    #auto interior doors
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            side = rooms_touch(rooms[i], rooms[j])
            if side:
                r = rooms[i]
                draw_door(
                    dwg,
                    r["x"] * scale,
                    r["y"] * scale,
                    r["w"] * scale,
                    r["h"] * scale,
                    side
                )

    #main exterior entrance
    entrance_room = max(rooms, key=lambda r: r["w"] * r["h"])
    draw_door(
        dwg,
        entrance_room["x"] * scale,
        entrance_room["y"] * scale,
        entrance_room["w"] * scale,
        entrance_room["h"] * scale,
        "bottom"
    )
    dwg.save()