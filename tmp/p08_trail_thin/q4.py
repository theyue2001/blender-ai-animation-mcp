import bpy, json, math
from mathutils import Vector, Matrix
GEN=r"""%GEN%"""
exec(GEN)
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
cam=bpy.data.objects["CAM_P08_01_Activation"]
lens=cam.data.lens; sw=cam.data.sensor_width
asp=sc.render.resolution_x/sc.render.resolution_y
MW=cam.matrix_world; M=MW.inverted()
camloc=MW.translation.copy()
Xax=Vector((MW[0][0],MW[1][0],MW[2][0])).normalized()
Yax=Vector((MW[0][1],MW[1][1],MW[2][1])).normalized()
fwd=-Vector((MW[0][2],MW[1][2],MW[2][2])).normalized()
K=(sw/2)/lens
def proj(p):
    q=M@Vector(p); d=-q.z
    hw=K*d; hh=hw/asp
    return (q.x/hw, q.y/hh, d)
def unproj(u,v,Ytarget):
    d=camloc.y-Ytarget
    for _ in range(6):
        p=camloc+fwd*d+Xax*(u*K*d)+Yax*(v*K*d/asp)
        err=p.y-Ytarget
        dd=(camloc+fwd*(d+1e-3)+Xax*(u*K*(d+1e-3))+Yax*(v*K*(d+1e-3)/asp)).y-p.y
        d-=err/(dd/1e-3)
    return camloc+fwd*d+Xax*(u*K*d)+Yax*(v*K*d/asp)

P0n=unproj(0.0,0.0,184.0)
B05=unproj(-0.26,-0.30,198.8)
P1n=unproj(0.30,0.20,217.1)
CC=2*B05-0.5*(P0n+P1n)
rep={"P0":[round(v,4) for v in P0n],"CC":[round(v,4) for v in CC],"P1":[round(v,4) for v in P1n]}
t0=2*(CC-P0n); t1=2*(P1n-CC)
def tilt(t):
    ax=abs(t.y); lat=math.sqrt(t.x**2+t.z**2)
    return round(math.degrees(math.atan2(lat,ax)),2)
rep["tilt_start"]=tilt(t0); rep["tilt_end"]=tilt(t1)
for nm,phase,rmul in [("BLUE",0.0,1.0),("PINK",math.pi+0.10,0.96)]:
    g,ln=build(P0n,CC,P1n,3.2,1.50,3.25,0.85,phase,rmul)
    pr=[proj(p) for p in g]
    rep[nm]={"len":round(ln,2),
      "start_screen":[round(pr[0][0],4),round(pr[0][1],4)],
      "end_screen":[round(pr[-1][0],3),round(pr[-1][1],3)],
      "bbox_x":[round(min(a[0] for a in pr),3),round(max(a[0] for a in pr),3)],
      "bbox_y":[round(min(a[1] for a in pr),3),round(max(a[1] for a in pr),3)],
      "dist":[round(min(a[2] for a in pr),2),round(max(a[2] for a in pr),2)],
      "offframe_pct":round(100.0*sum(1 for a in pr if abs(a[0])>1 or abs(a[1])>1)/len(pr),1)}
print(json.dumps(rep,indent=1))
