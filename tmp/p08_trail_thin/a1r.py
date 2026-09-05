import bpy, json, math
from mathutils import Vector, Matrix
GEN=r"""import math
from mathutils import Vector, Matrix
TWO=math.pi*2
def bez(P0,CC,P1,t):
    u=1-t
    return Vector(tuple(u*u*P0[i]+2*t*u*CC[i]+t*t*P1[i] for i in range(3)))
def build(P0,CC,P1,turns,r0,r1,rexp,phase,rmul,NS=4000,NOUT=520):
    ax=[bez(P0,CC,P1,i/(NS-1)) for i in range(NS)]
    L=[0.0]
    for i in range(1,NS): L.append(L[-1]+(ax[i]-ax[i-1]).length)
    tot=L[-1]; s=[v/tot for v in L]
    T=[]
    for i in range(NS):
        if i==0: d=ax[1]-ax[0]
        elif i==NS-1: d=ax[-1]-ax[-2]
        else: d=ax[i+1]-ax[i-1]
        T.append(d.normalized())
    up=Vector((0,0,1))
    n=(up-T[0]*up.dot(T[0])).normalized()
    Ns=[n]
    for i in range(1,NS):
        t0,t1=T[i-1],T[i]
        c=max(-1.0,min(1.0,t0.dot(t1))); axv=t0.cross(t1)
        if axv.length>1e-12 and c<1.0:
            n=n.copy(); n.rotate(Matrix.Rotation(math.acos(c),3,axv.normalized()))
            n=(n-t1*n.dot(t1)).normalized()
        Ns.append(n)
    pts=[]
    for i in range(NS):
        r=(r0+(r1-r0)*(s[i]**rexp))*rmul
        th=TWO*turns*s[i]+phase
        B=T[i].cross(Ns[i])
        pts.append(ax[i]+(Ns[i]*math.cos(th)+B*math.sin(th))*r)
    SL=[0.0]
    for i in range(1,NS): SL.append(SL[-1]+(pts[i]-pts[i-1]).length)
    total=SL[-1]; out=[]; j=0
    for k in range(NOUT):
        tg=total*k/(NOUT-1)
        while j<NS-2 and SL[j+1]<tg: j+=1
        seg=SL[j+1]-SL[j]
        f=0.0 if seg<=0 else (tg-SL[j])/seg
        out.append(pts[j].lerp(pts[j+1],f))
    return out,total
"""
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
