import sys, os, glob
from PIL import Image, ImageDraw
d, out, cols, rows = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
fs = sorted(glob.glob(os.path.join(d, "*.png")))
per = cols*rows
for s in range((len(fs)+per-1)//per):
    ch = fs[s*per:(s+1)*per]
    im0 = Image.open(ch[0]); w = 1900//cols; h = int(im0.height*w/im0.width)
    sh = Image.new("RGB", (w*cols, h*rows), (0,0,0)); dr = ImageDraw.Draw(sh)
    for k, f in enumerate(ch):
        im = Image.open(f).convert("RGB").resize((w,h), Image.LANCZOS)
        x, y = (k%cols)*w, (k//cols)*h
        sh.paste(im,(x,y))
        dr.text((x+4,y+3), os.path.basename(f).split("_")[1].split(".")[0], fill=(255,210,0))
    p = "%s_%d.png" % (out, s); sh.save(p); print(p, sh.size, len(ch))
