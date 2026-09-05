import bpy
from mathutils import Matrix
L=[]

def world_of(o):
    m = o.matrix_basis.copy()
    p = o.parent
    ch = o
    while p:
        m = p.matrix_basis @ ch.matrix_parent_inverse @ m
        ch = p; p = p.parent
    return m

def mat_info(o):
    out=[]
    for i,s in enumerate(o.material_slots):
        m=s.material
        if not m: out.append("  slot%d link=%s <none>"%(i,s.link)); continue
        bc=None; rough=None
        if m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type=='BSDF_PRINCIPLED':
                    bc=tuple(round(v,4) for v in n.inputs['Base Color'].default_value)
                    rough=round(n.inputs['Roughness'].default_value,3)
                    break
        out.append("  slot%d link=%-7s mat=%-46s users=%d base=%s rough=%s nodes=%s" % (
            i, s.link, m.name, m.users, bc, rough,
            [n.name for n in m.node_tree.nodes][:14] if m.use_nodes else "-"))
    return "\n".join(out)

for nm in ["WRN_DECAL_NITE_R1_Logo","P01_DECAL_NITE_R1_Logo_Reveal","DECAL_NITE_R1_Logo","X5_DECAL_NITE_R1_Logo","P04_DECAL_NITE_R1_Logo_Reveal"]:
    o=bpy.data.objects.get(nm)
    if not o: L.append("%s : MISSING"%nm); continue
    w=world_of(o)
    L.append("=== %s ===" % nm)
    L.append("  hide_v=%s hide_r=%s  parent=%s  colls=%s" % (o.hide_viewport,o.hide_render,o.parent.name if o.parent else "-",[c.name for c in o.users_collection]))
    L.append("  matrix_basis loc=%s scale=%s" % (tuple(round(v,5) for v in o.matrix_basis.translation), tuple(round(v,4) for v in o.matrix_basis.to_scale())))
    L.append("  WORLD loc=%s" % (tuple(round(v,5) for v in w.translation),))
    L.append(mat_info(o))
    ad=o.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            L.append("  FCU %s[%s]: %s" % (fc.data_path, fc.array_index, [(int(k.co[0]),round(k.co[1],3)) for k in fc.keyframe_points][:12]))
    else:
        L.append("  (no anim)")
    L.append("")

L.append("=== P05_WORN_ROOT ===")
r=bpy.data.objects["P05_WORN_ROOT"]
L.append("  loc=%s rot=%s scale=%s" % (tuple(round(v,4) for v in r.location), tuple(round(v,4) for v in r.rotation_euler), tuple(round(v,4) for v in r.scale)))
L.append("=== WRN_16_0.002 world ===")
o=bpy.data.objects["WRN_16_0.002"]
L.append("  world loc=%s  mat=%s" % (tuple(round(v,5) for v in world_of(o).translation), [s.material.name for s in o.material_slots]))
print("\n".join(L))
