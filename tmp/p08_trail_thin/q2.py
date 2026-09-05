import bpy, json, math
from mathutils import Vector
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
cam=bpy.data.objects["CAM_P08_01_Activation"]
res=[sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage]
lens=cam.data.lens; sw=cam.data.sensor_width; fit=cam.data.sensor_fit
aspect=res[0]/res[1]
M=cam.matrix_world.inverted()
def proj(p):
    q=M@Vector(p)             # cam space: -Z forward, +X right, +Y up
    d=-q.z
    if d<=0: return None
    hw=(sw/2)/lens*d
    hh=hw/aspect
    return (q.x/hw, q.y/hh, d)
out={"res":res,"lens":lens,"sw":sw,"fit":fit,"aspect":aspect,
     "cam_matrix":[[round(v,5) for v in r] for r in cam.matrix_world]}
for n in ["P08_TRAIL_BLUE","P08_TRAIL_PINK"]:
    o=bpy.data.objects[n]; sp=o.data.splines[0]
    pts=[o.matrix_world@Vector(p.co[:3]) for p in sp.points]
    N=len(pts)
    samp={}
    for f in [0,0.1,0.25,0.5,0.75,0.9,1.0]:
        i=min(N-1,int(f*(N-1)))
        p=pts[i]; s=proj(p)
        samp[f]={"world":[round(v,3) for v in p],"screen":[round(s[0],3),round(s[1],3)],"dist":round(s[2],2)}
    xs=[proj(p) for p in pts]
    out[n]={"samples":samp,
            "screen_bbox":[round(min(a[0] for a in xs),3),round(max(a[0] for a in xs),3),
                           round(min(a[1] for a in xs),3),round(max(a[1] for a in xs),3)],
            "dist_range":[round(min(a[2] for a in xs),2),round(max(a[2] for a in xs),2)]}
# taper curve shape
t=bpy.data.objects["P08_TRAIL_TAPER"].data.splines[0]
out["taper_pts"]=[[round(v,4) for v in (bp.co[:3] if hasattr(bp,'co') else bp.co[:3])] for bp in (t.bezier_points if t.bezier_points else t.points)]
out["taper_type"]=t.type
print(json.dumps(out,indent=1))
