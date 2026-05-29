import sys
import os
from PIL import Image, ImageDraw

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from algorithms import solve_vacuum

def draw_frame(M, N, grid, robot_pos, cell_size=60):
    width = N * cell_size
    height = M * cell_size
    img = Image.new("RGBA", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    
    for r in range(M):
        for c in range(N):
            x1 = c * cell_size
            y1 = r * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            
            # Sleek light grid tiles for high-quality visualization
            bg_color = "#f9f6f0" if (r + c) % 2 == 0 else "#f4efe6"
            draw.rectangle([x1, y1, x2, y2], fill=bg_color, outline="#dddddd")
            
            val = grid[r][c]
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            
            if val == -1: # Obstacle
                draw.rectangle([x1+4, y1+4, x2-4, y2-4], fill="#7f8c8d", outline="#34495e", width=2)
            elif val == 1: # Dirt
                r_blob = cell_size * 0.22
                draw.ellipse([cx-r_blob, cy-r_blob, cx+r_blob, cy+r_blob], fill="#e67e22")
                
    # Draw Robot
    r_robot, c_robot = robot_pos
    rx1 = c_robot * cell_size + cell_size * 0.15
    ry1 = r_robot * cell_size + cell_size * 0.15
    rx2 = rx1 + cell_size * 0.7
    ry2 = ry1 + cell_size * 0.7
    draw.ellipse([rx1, ry1, rx2, ry2], fill="#2980b9", outline="#1f3a52", width=3)
    
    # Inner circle representing robot head
    rcx = (rx1 + rx2) / 2
    rcy = (ry1 + ry2) / 2
    draw.ellipse([rcx-4, rcy-4, rcx+4, rcy+4], fill="#ffffff")
    
    return img

def make_gif_for_algorithm(algo, filename):
    M, N = 8, 8
    start_pos = (3, 7)
    
    dirty_cells = {(0,2),(1,6),(2,4),(3,1),(4,7),(5,2),(6,3),(7,5)}
    if start_pos in dirty_cells:
        dirty_cells.remove(start_pos)
        
    obstacles = {(1,1),(2,6),(4,2),(6,5),(7,3)}
    
    print(f"Solving and rendering for algorithm: {algo}...")
    result = solve_vacuum(M, N, start_pos, dirty_cells, obstacles, algo, style=2)
    
    if not result["found"]:
        print(f"  -> Path not found for {algo}!")
        return
        
    path = result["path"]
    
    # Rebuild the grid steps
    grid = [[0 for _ in range(N)] for _ in range(M)]
    for r, c in dirty_cells:
        grid[r][c] = 1
    for r, c in obstacles:
        grid[r][c] = -1
        
    frames = []
    
    # Render first frame
    frames.append(draw_frame(M, N, grid, start_pos))
    
    # Render subsequent frames
    current_pos = start_pos
    for step_pos in path[1:]:
        current_pos = step_pos
        if grid[current_pos[0]][current_pos[1]] == 1:
            grid[current_pos[0]][current_pos[1]] = 0 # clean dirt
        frames.append(draw_frame(M, N, grid, current_pos))
        
    # Create the gifs directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifs")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    
    # Save GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=400,
        loop=0
    )
    print(f"  -> Saved GIF successfully at: gifs/{filename} ({len(frames)} frames)")

def main():
    algos = ["BFS", "DFS", "UCS", "A*", "Greedy", "IDA*"]
    for algo in algos:
        safe_name = algo.lower().replace("*", "_star")
        filename = f"mayhutbui_{safe_name}.gif"
        make_gif_for_algorithm(algo, filename)
    print("\nDone! All GIF files have been created successfully in the 'gifs/' folder.")

if __name__ == "__main__":
    main()
