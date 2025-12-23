import svgwrite

scale = 20

def draw_blueprint(rooms, filename):
    dwg = svgwrite.Drawing(filename)

    #compute building boundaries for rooms later
    max_x = max(room["x"] + room["w"] for room in rooms)
    max_y = max(room["y"] + room["h"] for room in rooms)

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
            fill="none",
            stroke="black",
            stroke_width = 2
        ))

        dwg.add(dwg.text(
            room["name"],
            insert=((x + w) / 2, (y + h) / 2),
            text_anchor = "middle",
            alignment_baseline = "middle",
            font_size = 14
        ))

    #door example
    door_width = 3
    doors = []
    for room in rooms:
        if room["y"] == 0: #bottom wall
            doors.append({
                "x": (room["x"] + room["w"]) / 2 - door_width/ 2,
                "y": 0,
                "w": door_width,
                "h": 0
            })

    for door in doors:
        dwg.add(dwg.rect(
            insert=(door["x"] * scale, door["y"] * scale),
            size=(door["w"] * scale, 2),
            fill="white",
            stroke="none"
        ))  
    dwg.save()