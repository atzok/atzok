import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as nd
O='/tmp/claude-0/-home-user-atzok/a7300b2c-f040-526d-bd1b-320c27537490/scratchpad/adesivo'; F='/home/user/atzok/docs/lhama/carrossel-onde-o-clube/Adca.ttf'
reg=np.load(O+'/reg.npy'); H,W=reg.shape
art=Image.open(O+'/ref1.jpg').convert('RGB')
def disk(k):
    y,x=np.ogrid[-k:k+1,-k:k+1]; return x*x+y*y<=k*k
PINK=(230,121,211); CREAM=(242,234,216); INK=(21,21,21); LAVD=(78,87,194)
t='@LHAMABOOKINGS'
def pill(a, cx, cy, size, fill, txt, rot=0, stroke=False):
    f=ImageFont.truetype(F,size)
    tmp=Image.new('RGBA',(900,200),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    tw=d.textlength(t,font=f); h=size*1.55; x0=450-tw/2-size*0.6; x1=450+tw/2+size*0.6
    d.rounded_rectangle([x0+5,100-h/2+7,x1+5,100+h/2+7],radius=h/2,fill=LAVD+(255,))
    d.rounded_rectangle([x0,100-h/2,x1,100+h/2],radius=h/2,fill=fill+(255,),outline=INK+(255,),width=4)
    kw=dict(stroke_width=3,stroke_fill=INK) if stroke else {}
    d.text((450,102),t,font=f,fill=txt,anchor='mm',**kw)
    tmp=tmp.rotate(rot,expand=True,resample=Image.BICUBIC)
    a.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def mock(name, fn):
    a=art.copy(); fn(a)
    m=Image.fromarray((reg*255).astype(np.uint8))
    outer=nd.binary_dilation(reg,structure=disk(22))
    mo=Image.fromarray((outer*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))
    can=Image.new('RGB',(W,H),(205,201,192))
    can.paste(Image.new('RGB',(W,H),(150,145,135)),(10,14),mo.filter(ImageFilter.GaussianBlur(12)))
    can.paste(Image.new('RGB',(W,H),(252,251,248)),(0,0),mo)
    can.paste(a,(0,0),m.filter(ImageFilter.GaussianBlur(0.8)))
    edge=outer & ~nd.binary_erosion(outer,structure=disk(2))
    yy,xx=np.nonzero(edge); keep=((xx+yy)//10)%2==0
    arr=np.asarray(can).copy(); arr[yy[keep],xx[keep]]=(236,0,140)
    Image.fromarray(arr).save(O+'/%s.png'%name)
mock('opA', lambda a: pill(a,235,945,32,CREAM,INK,rot=-6))
mock('opB', lambda a: pill(a,700,430,36,PINK,CREAM,rot=8,stroke=True))
a=Image.open(O+'/opA.png').resize((540,675)); b=Image.open(O+'/opB.png').resize((540,675))
o=Image.new('RGB',(1100,675),'#eee'); o.paste(a,(0,0)); o.paste(b,(560,0)); o.save(O+'/adesivo-mpb-baixa.png')
