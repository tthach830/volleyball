from bs4 import BeautifulSoup
import re

def parse_svg():
    with open('c:/volleyball/VolleyballCourt.svg', 'r') as f:
        soup = BeautifulSoup(f.read(), 'xml')
    
    # Let's find all text or paths and see if they have ids or classes
    all_elements_with_id = soup.find_all(id=True)
    
    print(f"Found {len(all_elements_with_id)} elements with ID.")
    for el in all_elements_with_id[:20]:
        print(f"Tag: {el.name}, ID: {el['id']}")
        if el.name == 'g' or el.name == 'path':
            # print some hints about it
            print(f"  Attrs: {el.attrs}")

    # Let's also check if there are any specific structures after the image
    images = soup.find_all('image')
    print(f"Found {len(images)} images.")
    # Check what comes after the image
    if images:
        img = images[0]
        siblings = img.find_next_siblings()
        print(f"Found {len(siblings)} siblings after image.")
        for sib in siblings[:5]:
            print(f"Sibling tag: {sib.name}, attrs: {sib.attrs}")

if __name__ == '__main__':
    parse_svg()
