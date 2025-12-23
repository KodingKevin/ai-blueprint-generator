import svgwrite

scale = 20

def draw_blueprint(rooms, filename):
    dwg = svgwrite.Drawing(filename)

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
    dwg.save()