import bpy
from mathutils import Vector
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
out=[]
prev=bpy.context.window.scene
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
try:
    bpy.context.window.scene=sc
    tag="StrapUpper"
    ao=bpy.data.objects["NITE_%s_Armature"%tag]
    cuo=bpy.data.objects["CRV_%s_Path"%tag]
    ob=bpy.data.objects["P07_STRAP_UPPER"]
    W=ao.matrix_world.copy(); Wi=W.inverted()
    bps=cuo.data.splines[0].bezier_points; NCP=len(bps)
    Pw=[W@bps[i].co.copy() for i in range(NCP)]
    C=((min(p.x for p in Pw)+max(p.x for p in Pw))*.5,(min(p.y for p in Pw)+max(p.y for p in Pw))*.5)
    RAD=[]
    for p in Pw:
        d=Vector((p.x-C[0],p.y-C[1],0.0))
        RAD.append(d.normalized() if d.length>1e-6 else Vector((0,1,0)))
    # find a mesh vertex at the very tail tip (max rest s) to track
    me=ob.data
    vg=ob.vertex_groups["DEF_%s_23"%tag]
    tailv=[]
    for v in me.vertices:
        for g in v.groups:
            if g.group==vg.index and g.weight>0.9: tailv.append(v.index)
    tailv=tailv[:400]
    out.append("tracking %d tail verts (last deform bone)"%len(tailv))
    Mo=wmat(ob)
    def measure(label):
        dg=bpy.context.evaluated_depsgraph_get()
        ev=cuo.evaluated_get(dg); tm=ev.to_mesh()
        dn=[cuo.matrix_world@v.co.copy() for v in tm.vertices]
        L=sum((dn[j]-dn[j-1]).length for j in range(1,len(dn)))
        ev.to_mesh_clear()
        evo=ob.evaluated_get(dg); m2=evo.to_mesh()
        n=len(m2.vertices); d=[0.0]*(n*3); m2.vertices.foreach_get("co",d)
        pts=[Mo@Vector((d[3*i],d[3*i+1],d[3*i+2])) for i in tailv]
        cx=sum(p.x for p in pts)/len(pts); cy=sum(p.y for p in pts)/len(pts)
        allp=[Vector((d[3*i],d[3*i+1],d[3*i+2])) for i in range(0,n,37)]
        evo.to_mesh_clear()
        out.append("%-16s curveL=%.4f  tail-bone centroid=(%+.4f,%+.4f)"%(label,L,cx,cy))
        return L,cx,cy
    for pb in ao.pose.bones: pb.location=(0,0,0)
    sc.frame_set(1)
    base=measure("rest")
    for shrink in (0.02,0.05,0.09):
        for i in range(NCP):
            s=i/(NCP-1.0)
            # contract the loop everywhere except the two hardware zones
            w = 1.0
            if s<0.10: w=s/0.10
            if s>0.86: w=max(0.0,(0.94-s)/0.08)
            t=Pw[i]-RAD[i]*(shrink*w)
            pb=ao.pose.bones["%s_CP_%02d"%(tag,i)]
            delta=Wi.to_3x3()@(t-Pw[i])
            pb.location=pb.bone.matrix_local.to_3x3().inverted()@delta
        bpy.context.view_layer.update()
        L,cx,cy=measure("shrink %.3f"%shrink)
        out.append("     -> tail moved %.4f world units along the belt"%(((cx-base[1])**2+(cy-base[2])**2)**0.5))
    for pb in ao.pose.bones: pb.location=(0,0,0)
    bpy.context.view_layer.update()
finally:
    bpy.context.window.scene=prev
print("\n".join(out))
