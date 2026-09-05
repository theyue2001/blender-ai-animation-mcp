import bpy, math
from mathutils import Vector
C=(0.0589,-2.1837)
def bins(o):
    me=o.data; W=o.matrix_world
    n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
    d={}
    for i in range(n):
        v=W @ Vector((co[3*i],co[3*i+1],co[3*i+2]))
        a=math.degrees(math.atan2(v.y-C[1],v.x-C[0]))%360
        b=int(a//2.5)*2.5
        d[b]=d.get(b,0)+1
    return d
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis @ c.matrix_parent_inverse @ m; c=p; p=p.parent
    return m
src=bpy.data.objects["64.002"]; src_tmp=None
class P: pass
import types
oldW=wmat(src)
class Fake:
    def __init__(s,d,w): s.data=d; s.matrix_world=w
a=bins(Fake(src.data, oldW)); b=bins(bpy.data.objects["P07_STRAP_UPPER"])
print("bin  pre  post")
for k in sorted(set(list(a)+list(b))):
    if 100<=k<=135 or k<7.5 or k>355:
        print("%6.1f %6d %6d" % (k, a.get(k,0), b.get(k,0)))
print("TOTALS pre=%d post=%d" % (sum(a.values()), sum(b.values())))
