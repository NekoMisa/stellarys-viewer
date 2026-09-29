"""Convert the approved PNG into Windows icon assets; requires Pillow."""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[2]
icons = root / 'indra/newview/icons/stellarys'
master = Image.open(icons / 'stellarys-icon-master.png').convert('RGBA')
sizes = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
master.save(icons / 'firestorm_icon.ico', sizes=[(x,x) for x in sizes], bitmap_format='bmp')
for size in (16, 32, 48, 128, 256, 512):
    frame = master.resize((size,size), Image.Resampling.LANCZOS)
    frame.save(icons / ('firestorm_'+str(size)+'.png'))
    if size == 256: frame.convert('RGB').save(icons / 'firestorm_256.bmp')
ico = Image.open(icons / 'firestorm_icon.ico')
assert ico.info['sizes'] == {(x,x) for x in sizes}
print('Windows ICO frames verified:', sorted(ico.info['sizes']))
