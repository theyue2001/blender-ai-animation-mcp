from PIL import Image
import numpy as np
keys = {"top":(150,128),"centre":(150,170),"left":(110,170),"right":(192,170),"bottom":(150,212)}
imgs = {}
for f in (1340,1349,1378):
    im = Image.open("press_%d.png"%f).convert("RGB")
    imgs[f]=(im, np.asarray(im).astype(float))
print("crop size:", imgs[1340][0].size)
print("%-8s %s" % ("frame", "  ".join("%-8s"%k for k in keys)))
for f,(im,a) in imgs.items():
    row=[]
    for k,(cx,cy) in keys.items():
        p = a[cy-9:cy+9, cx-9:cx+9]
        row.append("%-8.1f" % p.mean())
    print("%-8d %s" % (f, "  ".join(row)))
print()
base = imgs[1340][1]
for f in (1349,1378):
    d = imgs[f][1] - base
    print("f%d vs f1340: max key delta = %s" % (f, {k: round(float((imgs[f][1][cy-9:cy+9,cx-9:cx+9]-base[cy-9:cy+9,cx-9:cx+9]).mean()),1) for k,(cx,cy) in keys.items()}))
