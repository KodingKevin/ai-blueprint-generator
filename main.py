from render_svg import draw_blueprint
from generator import generate_from_text

def main():
    user_input = "Small restaurant with 60 seats and a kitchen"
    
    rooms = generate_from_text(user_input)
    draw_blueprint(rooms, filename = "output.svg")
    
    print("Blueprint generated: output.svg")

if __name__ == "__main__":
    main()