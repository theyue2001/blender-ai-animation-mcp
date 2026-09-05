import bpy, bmesh, math
from mathutils import Vector, Matrix
SN="05_SCN_P07_STRAP_RIG"
sc=bpy.data.scenes[SN]; vl=sc.view_layers[0]
rig=bpy.data.collections["P07_RIG"]
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p:
        m=p.matrix_basis @ c.matrix_parent_inverse @ m; c=p; p=p.parent
    return m
def clean_mat(src, newname):
    m = src.copy(); m.name = newname
    if m.node_tree.animation_data: m.node_tree.animation_data_clear()
    if m.animation_data: m.animation_data_clear()
    nt=m.node_tree
    out=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'][0]
    pr =[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]
    for l in list(out.inputs['Surface'].links): nt.links.remove(l)
    nt.links.new(pr.outputs[0], out.inputs['Surface'])
    for n in [x for x in nt.nodes if "IGNITION" in x.name]: nt.nodes.remove(n)
    m.use_fake_user=False
    return m
SPECS=[("64.002","P07_STRAP_UPPER","ME_P07_STRAP_UPPER","MAT_P07_STRAP_UPPER",(0.0589,-2.1837),112.0),
       ("65.002","P07_STRAP_LOWER","ME_P07_STRAP_LOWER","MAT_P07_STRAP_LOWER",(0.0455,-2.3473),None)]
log=[]
for srcname,objname,mename,matname,C,cutang in SPECS:
    if objname in bpy.data.objects:
        log.append("%s exists, skip"%objname); continue
    src=bpy.data.objects[srcname]; W=wmat(src)
    me=src.data.copy(); me.name=mename
    ob=bpy.data.objects.new(objname, me)
    ob.matrix_world=W
    rig.objects.link(ob)
    mat=clean_mat(src.material_slots[0].material, matname)
    ob.material_slots[0].link='OBJECT'; ob.material_slots[0].material=mat
    # normals: clear custom split normals then re-shade by angle
    ctx=dict(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob], scene=sc, view_layer=vl)
    hadcn = me.has_custom_normals
    try:
        with bpy.context.temp_override(**ctx):
            if hadcn: bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
        nrm="cleared(%s)+smooth30"%hadcn
    except Exception as e:
        nrm="NORMALS_FAIL %s"%e
    # cut open the closed ring at a hidden seam under the buckle plate
    cut=""
    if cutang is not None:
        Wi=W.inverted()
        a=math.radians(cutang)
        rad_w=Vector((math.cos(a),math.sin(a),0.0))
        tan_w=Vector((-math.sin(a),math.cos(a),0.0))
        co_w=Vector((C[0],C[1],0.0))
        co_l=Wi @ co_w
        R3=Wi.to_3x3()
        no_l=(R3 @ tan_w).normalized()
        rad_l=(R3 @ rad_w).normalized()
        bm=bmesh.new(); bm.from_mesh(me)
        res=bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                                   dist=1e-4, plane_co=co_l, plane_no=no_l,
                                   clear_outer=False, clear_inner=False)
        cutedges=[]
        for g in res['geom_cut']:
            if isinstance(g, bmesh.types.BMEdge):
                mid=(g.verts[0].co+g.verts[1].co)*0.5
                if (mid-co_l).dot(rad_l) > 0.0: cutedges.append(g)
        bmesh.ops.split_edges(bm, edges=cutedges)
        bm.to_mesh(me); bm.free()
        cut="bisect@%.1fdeg cutedges=%d verts %d->%d"%(cutang,len(cutedges),len(src.data.vertices),len(me.vertices))
    log.append("%s: verts=%d polys=%d mat=%s normals=%s %s"%(objname,len(me.vertices),len(me.polygons),matname,nrm,cut))
# hide the un-rigged reference copies of the same straps
for n in ("P07R_64.002","P07R_65.002"):
    o=bpy.data.objects.get(n)
    if o: o.hide_render=True; o.hide_viewport=True
# body reference material so it is visible
bm_=bpy.data.materials.get("MAT_P07_BODY_REF")
if not bm_:
    bm_=bpy.data.materials.new("MAT_P07_BODY_REF"); bm_.use_nodes=True
    p=bm_.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value=(0.55,0.55,0.56,1); p.inputs["Roughness"].default_value=0.55
for n in ("P07R_Male","P07R_Underwear"):
    o=bpy.data.objects.get(n)
    if o and o.material_slots:
        o.material_slots[0].link='OBJECT'; o.material_slots[0].material=bm_
sc.frame_end=200
print("\n".join(log))
