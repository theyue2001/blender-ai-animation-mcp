import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
out=[]; prev=bpy.context.window.scene
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
def bvh_of(names):
    V=[];F=[]
    for nm in names:
        o=bpy.data.objects[nm]; M=wmat(o); me=o.data; b=len(V)
        n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
        for i in range(n): V.append(M@Vector((co[3*i],co[3*i+1],co[3*i+2])))
        for pg in me.polygons:
            vs=list(pg.vertices)
            for k in range(1,len(vs)-1): F.append((b+vs[0],b+vs[k],b+vs[k+1]))
    return BVHTree.FromPolygons(V,F,all_triangles=True,epsilon=0.0)
try:
    bpy.context.window.scene=sc
    HW=bvh_of(["P07R_58.002","P07R_59.002","P07R_60.002"])
    tag="StrapUpper"
    ao=bpy.data.objects["NITE_%s_Armature"%tag]
    cuo=bpy.data.objects["CRV_%s_Path"%tag]
    ob=bpy.data.objects["P07_STRAP_UPPER"]
    keep=ao.animation_data.action if ao.animation_data else None
    if keep: ao.animation_data.action=None
    W=ao.matrix_world.copy(); Wi=W.inverted()
    bps=cuo.data.splines[0].bezier_points; NCP=len(bps)
    Pw=[W@bps[i].co.copy() for i in range(NCP)]
    C=((min(p.x for p in Pw)+max(p.x for p in Pw))*.5,(min(p.y for p in Pw)+max(p.y for p in Pw))*.5)
    RAD=[(Vector((p.x-C[0],p.y-C[1],0.0)).normalized()) for p in Pw]
    me=ob.data; Mo=wmat(ob)
    vg=ob.vertex_groups["DEF_%s_23"%tag]
    tailv=[v.index for v in me.vertices if any(g.group==vg.index and g.weight>0.9 for g in v.groups)][:300]
    n=len(me.vertices)
    co0=[0.0]*(n*3); me.vertices.foreach_get("co",co0)
    used=set()
    for pg in me.polygons:
        for ek in pg.edge_keys: used.add(ek)
    eb=[0]*(len(me.edges)*2); me.edges.foreach_get("vertices",eb)
    ed=[(eb[2*k],eb[2*k+1]) for k in range(0,len(me.edges),9)
        if (min(eb[2*k],eb[2*k+1]),max(eb[2*k],eb[2*k+1])) in used][:20000]
    P0=[Vector((co0[3*i],co0[3*i+1],co0[3*i+2])) for i in range(n)]
    L0=[(P0[a]-P0[b]).length for a,b in ed]
    samp=list(range(0,n,17))[:6000]
    def measure(label):
        bpy.context.view_layer.update()
        dg=bpy.context.evaluated_depsgraph_get()
        ev=cuo.evaluated_get(dg); tm=ev.to_mesh()
        dn=[cuo.matrix_world@v.co.copy() for v in tm.vertices]
        L=sum((dn[j]-dn[j-1]).length for j in range(1,len(dn))); ev.to_mesh_clear()
        evo=ob.evaluated_get(dg); m2=evo.to_mesh()
        d=[0.0]*(n*3); m2.vertices.foreach_get("co",d)
        P=[Vector((d[3*i],d[3*i+1],d[3*i+2])) for i in range(n)]
        st=[abs((P[a]-P[b]).length-L0[k])/L0[k] for k,(a,b) in enumerate(ed) if L0[k]>1e-7]
        pts=[Mo@P[i] for i in tailv]
        cx=sum(p.x for p in pts)/len(pts); cy=sum(p.y for p in pts)/len(pts)
        ins=0
        for i in samp:
            o2=Mo@P[i]; c=0; org=o2+Vector((0,0,1e-5))
            while c<48:
                h=HW.ray_cast(org,Vector((0,0,1)),40.0)
                if h[0] is None: break
                org=h[0]+Vector((0,0,1e-5)); c+=1
            if c%2==1: ins+=1
        evo.to_mesh_clear()
        out.append("%-14s curveL=%.4f  tailC=(%+.4f,%+.4f)  stretch max=%.1f%% mean=%.3f%%  insideHW=%d/%d"
                   %(label,L,cx,cy,max(st)*100,sum(st)/len(st)*100,ins,len(samp)))
        return L,cx,cy
    for pb in ao.pose.bones: pb.location=(0,0,0)
    base=measure("REST")
    for shrink in (0.010,0.020,0.035,0.050):
        for i in range(NCP):
            s=i/(NCP-1.0); w=1.0
            if s<0.10: w=s/0.10
            if s>0.86: w=max(0.0,(0.94-s)/0.08)
            t=Pw[i]-RAD[i]*(shrink*w)
            pb=ao.pose.bones["%s_CP_%02d"%(tag,i)]
            pb.location=pb.bone.matrix_local.to_3x3().inverted()@(Wi.to_3x3()@(t-Pw[i]))
        L,cx,cy=measure("shrink %.3f"%shrink)
        out.append("    tail travel = %.4f  (%.1f x band width 0.232) ; curve vs chain 5.6095 -> %+.4f"
                   %(((cx-base[1])**2+(cy-base[2])**2)**0.5,
                     ((cx-base[1])**2+(cy-base[2])**2)**0.5/0.232, L-5.6095))
    for pb in ao.pose.bones: pb.location=(0,0,0)
    bpy.context.view_layer.update()
    if keep: ao.animation_data.action=keep
finally:
    bpy.context.window.scene=prev
print("\n".join(out))
