from parser import parse_text
from layout import generate_layout
from render_svg import draw_blueprint

def main():
    user_input = "Small restaurant with 60 seats and a kitchen"
    
    requirements = parse_text(user_input)
    rooms = generate_layout(requirements)
    draw_blueprint(rooms, filename = "output.svg")
    print("Blueprint generated: output.svg")

if __name__ == "__main__":
    main()