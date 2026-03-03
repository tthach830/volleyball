import re, base64

def extract():
    with open('c:/volleyball/VolleyballCourt.svg', 'r') as f:
        data = f.read()
    
    match = re.search(r'data:image/png;base64,([^\"\'\>]+)', data)
    if match:
        with open('c:/volleyball/map.png', 'wb') as f:
            f.write(base64.b64decode(match.group(1)))
        print("PNG extracted")
    else:
        print("No PNG found")

if __name__ == '__main__':
    extract()
