import matplotlib.pyplot as plt
from PIL import Image
import json
import os

coords = []
court_number = 1

def onclick(event):
    global court_number
    if event.xdata is not None and event.ydata is not None:
        coords.append({
            "court": f"Main Beach Volleyball Court {court_number:02d}",
            "x": int(event.xdata),
            "y": int(event.ydata)
        })
        print(f"Recorded Court {court_number} at ({int(event.xdata)}, {int(event.ydata)})")
        
        # Draw a little red dot where they clicked to confirm
        plt.plot(event.xdata, event.ydata, 'ro')
        plt.draw()
        
        court_number += 1
        
        if court_number > 18:
            print("All 18 courts recorded! Saving to court_coords.json and closing...")
            with open('c:/volleyball/court_coords.json', 'w') as f:
                json.dump(coords, f, indent=4)
            plt.close()

def calibrate():
    print("Loading map.png...")
    if not os.path.exists('c:/volleyball/map.png'):
        print("Error: map.png not found!")
        return
        
    img = Image.open('c:/volleyball/map.png')
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(img)
    ax.set_title('Click on Court 1, then Court 2, up to 18')
    
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    
    print("Please click on each of the 18 courts in order.")
    plt.show()

if __name__ == '__main__':
    calibrate()
