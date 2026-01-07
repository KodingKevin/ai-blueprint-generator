from parser import parse_text
from templates import get_template
from layout import generate_layout
from render_svg import draw_blueprint

def main():
    user_input = "2 bedroom house with 2 bathrooms and a kitchen"
    req = parse_text(user_input)

    template_rooms = get_template(req["building_type"], req)
    rooms = generate_layout(req, template_rooms)

    draw_blueprint(rooms, filename="output.svg")
    print("Blueprint generated: output.svg")

if __name__ == "__main__":
    main()