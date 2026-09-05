import bpy, math
from mathutils import Vector
SN="05_SCN_P07_STRAP_RIG"
out=[]
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
def wverts(nm):
    o=bpy.data.objects[nm]; M=wmat(o); me=o.data
    n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
    return [M@Vector((co[3*i],co[3*i+1],co[3*i+2])) for i in range(n)]

BOX={"59.002":((0.033,0.501),(-1.593,-1.443),(0.832,1.203)),
     "60.002":((-0.433,-0.063),(-1.583,-1.486),(0.831,1.203)),
     "63.002":((-0.320,-0.173),(-1.544,-1.485),(0.128,0.354)),
     "64.005":((0.270,0.418),(-1.544,-1.485),(0.128,0.354))}
SLOT={"60.002":("X",(-1.579,-1.549),(0.888,1.147)),
      "63.002":("Y",(-0.293,-0.256),(0.158,0.323)),
      "64.005":("Y",(0.353,0.390),(0.158,0.323))}

for src,tag in (("64.002","UPPER"),("65.002","LOWER")):
    P=wverts(src)
    C=((min(p.x for p in P)+max(p.x for p in P))*.5,(min(p.y for p in P)+max(p.y for p in P))*.5)
    out.append("")
    out.append("=== %s (%s)  n=%d  centre=(%.3f,%.3f) ==="%(src,tag,len(P),C[0],C[1]))
    for hw,(bx,by,bz) in BOX.items():
        ins=[p for p in P if bx[0]<=p.x<=bx[1] and by[0]<=p.y<=by[1] and bz[0]<=p.z<=bz[1]]
        if not ins:
            out.append("  vs %-9s : 0 verts inside its bbox"%hw); continue
        ang=[math.degrees(math.atan2(p.y-C[1],p.x-C[0]))%360.0 for p in ins]
        out.append("  vs %-9s : %d verts inside bbox, angle %.1f..%.1f, x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f"
                   %(hw,len(ins),min(ang),max(ang),min(p.x for p in ins),max(p.x for p in ins),
                     min(p.y for p in ins),max(p.y for p in ins),min(p.z for p in ins),max(p.z for p in ins)))
        if hw in SLOT:
            ax,ra,rb=SLOT[hw]
            if ax=="X": sel=[p for p in ins if ra[0]<=p.y<=ra[1] and rb[0]<=p.z<=rb[1]]
            else:       sel=[p for p in ins if ra[0]<=p.x<=ra[1] and rb[0]<=p.z<=rb[1]]
            out.append("       -> verts INSIDE the thru-%s slot: %d"%(ax,len(sel)))
    # open ends
    me=bpy.data.objects[src].data
    ec={}
    for pg in me.polygons:
        for e in pg.edge_keys: ec[e]=ec.get(e,0)+1
    bd=set()
    for e,c in ec.items():
        if c==1: bd.update(e)
    if bd:
        bp=[P[i] for i in bd]
        ba=[math.degrees(math.atan2(p.y-C[1],p.x-C[0]))%360.0 for p in bp]
        # cluster angles
        sa=sorted(ba); grp=[[sa[0]]]
        for a in sa[1:]:
            if a-grp[-1][-1]>5.0: grp.append([a])
            else: grp[-1].append(a)
        out.append("  boundary(open-end) verts=%d in %d cluster(s):"%(len(bd),len(grp)))
        for g in grp:
            sub=[p for p,a in zip(bp,ba) if g[0]-1e-9<=a<=g[-1]+1e-9]
            out.append("     ang %.1f..%.1f  n=%d  x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f"
                       %(g[0],g[-1],len(sub),min(p.x for p in sub),max(p.x for p in sub),
                         min(p.y for p in sub),max(p.y for p in sub),min(p.z for p in sub),max(p.z for p in sub)))
    else:
        out.append("  no boundary edges -> CLOSED ring")
print("\n".join(out))
