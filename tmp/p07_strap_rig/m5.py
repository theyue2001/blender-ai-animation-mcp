import bpy, math
from mathutils import Vector
out=[]
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
def wv(nm):
    o=bpy.data.objects[nm]; M=wmat(o); me=o.data
    n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
    return [M@Vector((co[3*i],co[3*i+1],co[3*i+2])) for i in range(n)]
S=wv("64.002")
HW={"59":wv("P07R_59.002"),"60":wv("P07R_60.002")}
Y0,Y1=-1.68,-1.42; Z0,Z1=0.80,1.24
NW,NH=52,26
for x in (-0.55,-0.45,-0.38,-0.30,-0.26,-0.20,-0.10,0.00,0.05,0.15,0.30,0.45,0.52):
    grid=[[" "]*NW for _ in range(NH)]
    def put(pts,ch):
        for p in pts:
            if abs(p.x-x)>0.008: continue
            if not(Y0<=p.y<=Y1 and Z0<=p.z<=Z1): continue
            c=int((p.y-Y0)/(Y1-Y0)*(NW-1)); r=NH-1-int((p.z-Z0)/(Z1-Z0)*(NH-1))
            if grid[r][c] in (" ",) or ch=="#": grid[r][c]=ch
    for k,v in HW.items(): put(v,"." if k=="60" else ",")
    put(S,"#")
    ns=sum(row.count("#") for row in grid)
    out.append("")
    out.append("x=%+.2f   ('#'=strap  '.'=60.002  ','=59.002)   y:%.2f->%.2f  z:%.2f->%.2f"%(x,Y0,Y1,Z1,Z0))
    for r in range(NH): out.append("   |"+"".join(grid[r])+"|")
print("\n".join(out))
