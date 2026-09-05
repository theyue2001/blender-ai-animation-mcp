from PIL import Image
import numpy as np

def stats(path, box, label):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(float)
    x0,y0,x1,y1 = box
    r = a[y0:y1, x0:x1]
    lum = r.mean(axis=2)
    # logo pixels = the bright cluster
    thr = max(lum.max()*0.45, 40)
    m = lum > thr
    print("%-14s img=%s crop=%s  logo px=%d  mean RGB=%s  p90 lum=%.1f  max=%.1f  bg mean=%.1f" % (
        label, im.size, box, m.sum(),
        tuple(round(v,1) for v in r[m].mean(axis=0)) if m.sum() else None,
        np.percentile(lum[m],90) if m.sum() else -1, lum.max(), lum[~m].mean()))

stats("fix_1396.png",   (130, 190, 200, 260), "ACT3 f1396")
stats("ref_s01_340.png",(130,  55, 235, 160), "SCN01 f340")
