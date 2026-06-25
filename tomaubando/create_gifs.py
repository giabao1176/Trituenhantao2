import sys
import os
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import districts, neighbors, coordinates, colors, color_hex
from algorithms import solve_backtracking_stepwise, solve_forward_checking_stepwise, solve_ac3_stepwise, solve_min_conflicts_stepwise

def draw_tphcm_frame(assignment, highlight_var=None, algo_name="", step_num=0):
    width, height = 700, 750
    img = Image.new("RGBA", (width, height), "#f8f9fa")
    draw = ImageDraw.Draw(img)

    try:
        label_font = ImageFont.truetype("arial.ttf", 12)
        status_font = ImageFont.truetype("arial.ttf", 18)
        status_text = f"Thuật toán: {algo_name} | Bước: {step_num}"
    except IOError:
        label_font = ImageFont.load_default()
        status_font = ImageFont.load_default()
        status_text = f"Algo: {algo_name} | Step: {step_num}"

    for node, adjs in neighbors.items():
        if node in coordinates:
            x1, y1 = coordinates[node]
            for adj in adjs:
                if adj in coordinates:
                    x2, y2 = coordinates[adj]
                    draw.line([(x1, y1), (x2, y2)], fill="#dcdde1", width=2)

    r = 20
    for node, (x, y) in coordinates.items():
        color = assignment.get(node)
        hex_color = color_hex.get(color, "#ffffff")

        outline_color = "#e74c3c" if node == highlight_var else "#353b48"
        outline_width = 4 if node == highlight_var else 2

        draw.ellipse([x - r, y - r, x + r, y + r], fill=hex_color, outline=outline_color, width=outline_width)

        label = node.replace("Quận ", "Q.")
        draw.text((x - 15, y + r + 4), label, fill="#2f3640", font=label_font)

    draw.rectangle([0, 710, width, height], fill="#2c3e50")
    draw.text((15, 720), status_text, fill="#ffffff", font=status_font)

    return img

def make_gif(algo_name, generator_func, filename):
    print(f"Generating GIF for Map Coloring: {algo_name}...")

    steps_generator = generator_func(districts, neighbors, colors)
    frames = []

    frames.append(draw_tphcm_frame({}, algo_name=algo_name, step_num=0))

    step_count = 0
    max_frames = 60

    for step in steps_generator:
        if step.get("action") == "ac3_revise":
            continue

        highlight = step.get("var")
        assignment = step.get("assignment", {})
        step_count += 1
        frames.append(draw_tphcm_frame(assignment, highlight, algo_name=algo_name, step_num=step_count))
        if step_count >= max_frames:
            break

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=450,
        loop=0
    )
    print(f"  -> Saved successfully at: gifs/{filename} ({len(frames)} frames)")

def main():
    make_gif("Backtracking", solve_backtracking_stepwise, "tomaubando_backtracking.gif")
    make_gif("Forward Checking", solve_forward_checking_stepwise, "tomaubando_forward_checking.gif")
    make_gif("AC-3 + MAC", solve_ac3_stepwise, "tomaubando_ac3.gif")
    make_gif("Min-Conflicts", solve_min_conflicts_stepwise, "tomaubando_min_conflicts.gif")
    print("\nDone! All Map Coloring GIF files have been created successfully in 'gifs/' folder.")

if __name__ == "__main__":
    main()
