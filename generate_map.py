import sqlite3
import json
import os
from PIL import Image, ImageDraw

def generate_map():
    coords_file = 'court_coords.json'
    if not os.path.exists(coords_file):
        print("Coordinates not found! Please run calibrate_map.py first.")
        return
        
    with open(coords_file, 'r') as f:
        courts_coords = json.load(f)
        
    print("Coordinates loaded. Querying database for availability...")
    
    conn = sqlite3.connect('volleyball.db')
    c = conn.cursor()
    
    import datetime
    now = datetime.datetime.now()
    current_hour = now.hour
    
    h1 = current_hour % 12
    if h1 == 0: h1 = 12
    am1 = "am" if current_hour < 12 else "pm"
    
    h2 = (current_hour + 1) % 12
    if h2 == 0: h2 = 12
    am2 = "am" if (current_hour + 1) < 12 or (current_hour + 1) == 24 else "pm"
    
    current_slot = f"{h1}{am1}-{h2}{am2}"
    target_slots = [current_slot]
    
    court_availability = {}
    
    # Check each court
    for court_data in courts_coords:
        court_name = court_data['court']
        
        # Default to available
        is_available = True
        
        c.execute("SELECT id FROM courts WHERE name = ?", (court_name,))
        res = c.fetchone()
        
        if res:
            court_id = res[0]
            
            # If any of the target slots are unavailable, mark the court as unavailable for this period
            target_date_str = now.strftime("%Y-%m-%d")
            for slot in target_slots:
                c.execute("SELECT status FROM slots WHERE court_id = ? AND time_slot = ? AND (date = ? OR date IS NULL)", (court_id, slot, target_date_str))
                status_res = c.fetchone()
                if status_res and status_res[0] == 'unavailable':
                    is_available = False
                    break
        else:
            print(f"Warning: {court_name} not found in database.")
            
        court_availability[court_name] = is_available
        
    conn.close()
    
    print("Database queried. Drawing map...")
    
    # Open the map image
    img = Image.open('map.png').convert("RGBA")
    
    # Create a semi-transparent overlay
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Circle radius
    r = 25
    
    # Try to load a generic font or fallback to default
    try:
        from PIL import ImageFont
        # 1. Try Windows font path
        # 2. Try common Ubuntu/Linux font paths
        # 3. Fallback to default
        font_paths = [
            "arialbd.ttf",                               # Windows / Local
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", # Ubuntu (Actions)
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", # Ubuntu Alternative
        ]
        
        font = None
        for path in font_paths:
            try:
                font = ImageFont.truetype(path, 20)
                print(f"Loaded font from: {path}")
                break
            except:
                continue
        
        if font is None:
            print("No custom font found, using default.")
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
        
    for court_data in courts_coords:
        court_name = court_data['court']
        court_num = str(int(court_name.split()[-1]))
        x = court_data['x']
        y = court_data['y']
        
        available = court_availability.get(court_name, True)
        
        if available:
            # Green, semi-transparent
            color = (0, 255, 0, 150)
        else:
            # Red, semi-transparent
            color = (255, 0, 0, 150)
            
        # Draw ellipse bounding box
        bbox = [x - r, y - r, x + r, y + r]
        draw.ellipse(bbox, fill=color, outline=(0,0,0,255), width=2)
        
        # Draw court number text below the dot
        text_str = f"Court {court_num}"
        # We can approximate width or use getbbox
        try:
            text_bbox = font.getbbox(text_str)
            text_width = text_bbox[2] - text_bbox[0]
        except AttributeError:
            # Fallback for older Pillow
            text_width = 50
            
        # Position slightly below the circle
        text_x = x - (text_width / 2)
        text_y = y + r + 5
        
        draw.text((text_x, text_y), text_str, fill=(0, 0, 0, 255), font=font)
        
    # Combine the images
    img_with_overlay = Image.alpha_composite(img, overlay)
    
    # Save the output
    output_path = 'map_status.png'
    img_with_overlay.save(output_path)
    print(f"Success! Colored map saved to {output_path}")

if __name__ == '__main__':
    generate_map()
