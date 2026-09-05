import bpy, json, math
from mathutils import Vector, Matrix
GEN=r"""%GEN%"""
exec(GEN)
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
cam=bpy.data.objects["CAM_P08_01_Activation"]
lens=cam.data.lens; sw=cam.data.sensor_width
asp=sc.render.resolution_x/sc.render.resolution_y
MW=cam.matrix_world; M=MW.inverted(); camloc=MW.translation.copy()
Xax=Vector((MW[0][0],MW[1][0],MW[2][0])).normalized()
Yax=Vector((MW[0][1],MW[1][1],MW[2][1])).normalized()
fwd=-Vector((MW[0][2],MW[1][2],MW[2][2])).normalized()
K=(sw/2)/lens
def unproj(u,v,Yt):
    d=camloc.y-Yt
    for _ in range(6):
        p=camloc+fwd*d+Xax*(u*K*d)+Yax*(v*K*d/asp)
        e=p.y-Yt
        dd=(camloc+fwd*(d+1e-3)+Xax*(u*K*(d+1e-3))+Yax*(v*K*(d+1e-3)/asp)).y-p.y
        d-=e/(dd/1e-3)
    return camloc+fwd*d+Xax*(u*K*d)+Yax*(v*K*d/asp)
P0n=unproj(0.0,0.0,184.0); B05=unproj(-0.26,-0.30,198.8); P1n=unproj(0.30,0.20,217.1)
CC=2*B05-0.5*(P0n+P1n)

log={}
NEW_BEVEL=0.105
for name,phase,rmul in [("P08_TRAIL_BLUE",0.0,1.0),("P08_TRAIL_PINK",math.pi+0.10,0.96)]:
    o=bpy.data.objects[name]; sp=o.data.splines[0]
    assert len(sp.points)==520, (name,len(sp.points))
    g,ln=build(P0n,CC,P1n,3.2,1.50,3.25,0.85,phase,rmul)
    old_bev=o.data.bevel_depth
    for i,p in enumerate(sp.points):
        p.co=(g[i].x,g[i].y,g[i].z,1.0)
    o.data.bevel_depth=NEW_BEVEL
    o.data.update_tag()
    log[name]={"bevel":[round(old_bev,4),round(o.data.bevel_depth,4)],
               "strand_len":round(ln,2),
               "p0":[round(v,3) for v in g[0]],"p_end":[round(v,3) for v in g[-1]]}
log["axis"]={"P0":[round(v,4) for v in P0n],"CC":[round(v,4) for v in CC],"P1":[round(v,4) for v in P1n]}
print(json.dumps(log,indent=1))
