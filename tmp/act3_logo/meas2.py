from PIL import Image
import numpy as np
def dome(path, box, label):
    im = Image.open(path).convert("RGB"); a=np.asarray(im).astype(float)
    x0,y0,x1,y1 = box
    r = a[y0:y1, x0:x1]; lum = r.mean(axis=2)
    # exclude the logo (very bright small cluster) from the shell stats
    sh = lum[lum < 150]
    print("%-22s size=%-11s dome px=%6d  mean=%5.1f  p95=%5.1f  p99=%5.1f  max=%5.1f  |  hot>60: %5.2f%%  hot>90: %5.2f%%" % (
        label, im.size, sh.size, sh.mean(), np.percentile(sh,95), np.percentile(sh,99), lum.max(),
        100*(sh>60).mean(), 100*(sh>90).mean()))
for p in ("fix_1396.png","mat_dev_1396.png","s01_dev_340.png"):
    print(p, Image.open(p).size)
print()
dome("fix_1396.png",     ( 70,120, 270,290), "BEFORE act3 (smoked)")
dome("mat_dev_1396.png", ( 90,145, 285,300), "AFTER  act3 (scn01)")
dome("s01_dev_340.png",  (165, 60, 500,380), "REF    scene 01")
