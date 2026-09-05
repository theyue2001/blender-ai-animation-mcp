import bpy, math
from mathutils import Vector
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=sc; sc.frame_set(1434)
    dg=bpy.context.evaluated_depsgraph_get()
    cam=sc.camera.evaluated_get(dg); mw=cam.matrix_world; org=mw.translation
    tr,br,bl,tl = sc.camera.data.view_frame(scene=sc)
    def ray(px,py):
        u,v = px/1920.0, py/1080.0
        p = tl.lerp(tr,u).lerp(bl.lerp(br,u), v)
        return (mw@p - org).normalized()
    AX, AY = 0.0493, -0.3201
    samples = [("band-centre",1368,372),("band-left-of-cut",1320,372),("just-left-outside",1310,372),
               ("band-right-end",1428,372),("just-right-outside",1440,372),
               ("above-band",1368,342),("below-band",1368,405)]
    for lab,px,py in samples:
        d=ray(px,py); o=org.copy()
        print("--- %s  px(%d,%d)"%(lab,px,py))
        for k in range(6):
            hit,loc,nor,idx,obj,m = sc.ray_cast(dg,o,d)
            if not hit: break
            r=math.hypot(loc.x-AX, loc.y-AY)
            print("      %-26s z=%.4f r=%.4f  n=(%.2f,%.2f,%.2f) |nz|=%.2f" % (
                obj.name.replace("X5_",""), loc.z, r, nor.x,nor.y,nor.z, abs(nor.z)))
            o=loc+d*1e-4
finally:
    win.scene=prev
