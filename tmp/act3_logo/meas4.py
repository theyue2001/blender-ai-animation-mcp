from PIL import Image
import numpy as np
keys = {"top":(150,128),"centre":(150,170),"left":(110,170),"right":(192,170),"bottom":(150,212)}
def val(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)
    return {k: float(a[cy-9:cy+9, cx-9:cx+9].mean()) for k,(cx,cy) in keys.items()}
print("%-10s %-8s %-8s %-8s %s" % ("variant","frame","centre","neighb","centre-neighb (press contrast)"))
for tag,label in (("oldbase","OLD dark"),("press","NEW scn01")):
    for f in (1340,1349,1378):
        v = val("%s_%d.png" % (tag,f))
        nb = np.mean([v[k] for k in ("top","left","right","bottom")])
        print("%-10s %-8d %-8.1f %-8.1f %+.1f" % (label,f,v["centre"],nb,v["centre"]-nb))
    print()
