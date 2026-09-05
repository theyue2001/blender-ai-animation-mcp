import bpy
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
fps=sc.render.fps
BEATS=[("1:00-1:08 space station",1440,1632),
       ("1:08-1:16 NITE structure, slow rotation in place",1632,1824),
       ("1:16-1:24 unit joins belt / lock close-up / belt through buckle",1824,2016),
       ("1:24-1:30 hands leave device, free your hands",2016,2160)]
print("scene %s  fps=%d  range %d-%d"%(SN,fps,sc.frame_start,sc.frame_end))
print("timecode check: frame/fps -> 1632=%.2fs 1824=%.2fs 2016=%.2fs 2160=%.2fs"
      %(1632/fps,1824/fps,2016/fps,2160/fps))
print("markers:",[(m.frame,m.name) for m in sorted(sc.timeline_markers,key=lambda m:m.frame)])
anim=[]
for o in sc.objects:
    for holder,lbl in ((o,"obj"),(o.data if o.type in ('CAMERA','LIGHT') else None,"data")):
        if holder is None: continue
        ad=getattr(holder,"animation_data",None)
        if ad and ad.action:
            ks=sorted({round(k.co[0]) for fc in ad.action.fcurves for k in fc.keyframe_points})
            anim.append((o.name,lbl,ad.action.name,ks))
print()
for nm,lo,hi in BEATS:
    print("=== %s  (frames %d-%d) ==="%(nm,lo,hi))
    hit=False
    for on,lbl,an,ks in anim:
        inr=[k for k in ks if lo<=k<=hi]
        if len(inr)>=2:
            print("   %-24s %-8s %-24s keys in range: %s"%(on,lbl,an,inr))
            hit=True
    if not hit:
        print("   >>> NOTHING ANIMATED IN THIS RANGE <<<")
    print()
