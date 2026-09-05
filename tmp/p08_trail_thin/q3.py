import bpy, json, math
from mathutils import Vector
TWO=math.pi*2
def bez(P0,CC,P1,t):
    u=1-t
    return Vector((u*u*P0[i]+2*t*u*CC[i]+t*t*P1[i] for i in range(3)))
def build(P0,CC,P1,turns,r0,r1,rexp,phase,rmul,NS=4000,NOUT=520):
    # dense axis samples + arclength
    ax=[bez(P0,CC,P1,i/(NS-1)) for i in range(NS)]
    L=[0.0]
    for i in range(1,NS): L.append(L[-1]+(ax[i]-ax[i-1]).length)
    tot=L[-1]; s=[v/tot for v in L]
    # tangents
    T=[]
    for i in range(NS):
        if i==0: d=ax[1]-ax[0]
        elif i==NS-1: d=ax[-1]-ax[-2]
        else: d=ax[i+1]-ax[i-1]
        T.append(d.normalized())
    # parallel transport frame
    up=Vector((0,0,1))
    n=(up-T[0]*up.dot(T[0])).normalized()
    Ns=[n]
    for i in range(1,NS):
        t0,t1=T[i-1],T[i]
        c=max(-1.0,min(1.0,t0.dot(t1)))
        ax_=t0.cross(t1)
        if ax_.length>1e-12 and c<1.0:
            n=n.copy(); n.rotate(__import__("mathutils").Matrix.Rotation(math.acos(c),3,ax_.normalized()))
            n=(n-t1*n.dot(t1)).normalized()
        Ns.append(n)
    pts=[]
    for i in range(NS):
        r=(r0+(r1-r0)*(s[i]**rexp))*rmul
        th=TWO*turns*s[i]+phase
        B=T[i].cross(Ns[i])
        pts.append(ax[i]+ (Ns[i]*math.cos(th)+B*math.sin(th))*r)
    # resample to uniform arc length
    SL=[0.0]
    for i in range(1,NS): SL.append(SL[-1]+(pts[i]-pts[i-1]).length)
    total=SL[-1]; out=[]; j=0
    for k in range(NOUT):
        target=total*k/(NOUT-1)
        while j<NS-2 and SL[j+1]<target: j+=1
        seg=SL[j+1]-SL[j]
        f=0.0 if seg<=0 else (target-SL[j])/seg
        out.append(pts[j].lerp(pts[j+1],f))
    return out,total

OLD=dict(P0=(13,184,-5.8),CC=(-2,199,-9),P1=(-4.2,217,2.4))
rep={}
for name,phase,rmul in [("P08_TRAIL_BLUE",0.0,1.0),("P08_TRAIL_PINK",math.pi+0.10,0.96)]:
    gen,ln=build(OLD["P0"],OLD["CC"],OLD["P1"],3.2,1.50,3.25,0.85,phase,rmul)
    o=bpy.data.objects[name]; sp=o.data.splines[0]
    cur=[Vector(p.co[:3]) for p in sp.points]
    dev=[(gen[i]-cur[i]).length for i in range(min(len(gen),len(cur)))]
    rep[name]={"n_gen":len(gen),"n_cur":len(cur),"len":round(ln,3),
               "max_dev":round(max(dev),4),"mean_dev":round(sum(dev)/len(dev),4)}
# also: who rides these paths?
riders=[]
for o in bpy.data.objects:
    for c in o.constraints:
        if getattr(c,'target',None) and c.target.name in ("P08_TRAIL_BLUE","P08_TRAIL_PINK"):
            riders.append((o.name,c.type,c.target.name,round(getattr(c,'offset_factor',-1),4)))
rep["riders"]=riders
print(json.dumps(rep,indent=1))
