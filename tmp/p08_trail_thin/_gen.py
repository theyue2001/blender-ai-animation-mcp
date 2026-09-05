import math
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
