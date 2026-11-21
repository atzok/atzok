# gera ../contact-sheet.png a partir de card-01..10.png
from PIL import Image, ImageDraw, ImageFont
import os
d0=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
W,H=1080,1350; s=0.4; tw,th=int(W*s),int(H*s); g=24
sheet=Image.new('RGB',(tw*5+g*6,th*2+g*3+60),(24,24,22)); d=ImageDraw.Draw(sheet)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',22)
for i in range(10):
  im=Image.open(f'{d0}/card-{i+1:02d}.png').convert('RGB').resize((tw,th),Image.LANCZOS)
  x=g+(i%5)*(tw+g); y=g+(i//5)*(th+g+30)
  sheet.paste(im,(x,y)); d.text((x,y+th+6),f'{i+1:02d}',fill=(200,200,190),font=f)
sheet.save(f'{d0}/contact-sheet.png')
