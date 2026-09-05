import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=sc; sc.frame_set(1434)
    dg=bpy.context.evaluated_depsgraph_get()
    cam=sc.camera.evaluated_get(dg); mw=cam.matrix_world
    tr,br,bl,tl = sc.camera.data.view_frame(scene=sc)
    org=mw.translation
    # circled region in full-frame px (1920x1080)
    X0,X1,Y0,Y1 = 1256,1500,280,495
    from collections import Counter
    cnt=Counter(); first=Counter(); rows=[]
    N=13
    for iy in range(N):
        row=[]
        for ix in range(N):
            u=(X0+(X1-X0)*ix/(N-1))/1920.0
            v=(Y0+(Y1-Y0)*iy/(N-1))/1080.0
            p_cam = tl.lerp(tr,u).lerp(bl.lerp(br,u), v)
            d=(mw@p_cam - org).normalized()
            o=org.copy(); chain=[]
            for k in range(10):
                hit,loc,nor,idx,obj,m = sc.ray_cast(dg,o,d)
                if not hit: break
                chain.append(obj.name); cnt[obj.name]+=1
                o=loc+d*1e-4
            if chain: first[chain[0]]+=1
            row.append(chain[0].replace("X5_","")[:9] if chain else "-")
        rows.append(" ".join("%-9s"%c for c in row))
    print("FIRST-HIT map over the circled region (x %d-%d, y %d-%d):"%(X0,X1,Y0,Y1))
    print("\n".join(rows))
    print()
    print("first hits:", first.most_common())
    print("all hits  :", cnt.most_common())
finally:
    win.scene=prev
