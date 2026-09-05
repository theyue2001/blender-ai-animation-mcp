import bpy
from mathutils import Vector
out = []

o = bpy.data.objects["INST_Opening_Human"]
out.append("INST_Opening_Human  type=%s inst_type=%s coll=%s" %
           (o.type, o.instance_type, o.instance_collection.name if o.instance_collection else None))
out.append("  matrix_world loc=%s rot=%s scale=%s" %
           (tuple(round(v, 4) for v in o.matrix_world.translation),
            tuple(round(v, 4) for v in o.rotation_euler),
            tuple(round(v, 4) for v in o.scale)))
out.append("  library=%s" % (o.instance_collection.library.filepath if o.instance_collection and o.instance_collection.library else "LOCAL"))

def walk(c, d=0):
    out.append("%s+ COLL %-32s objs=%d children=%d" % ("  " * (d + 1), c.name, len(c.objects), len(c.children)))
    for ob in sorted(c.objects, key=lambda x: x.name):
        nv = len(ob.data.vertices) if ob.type == 'MESH' else '-'
        try:
            bb = [ob.matrix_world @ Vector(cc) for cc in ob.bound_box]
            dim = "dim=(%.3f,%.3f,%.3f) ctr=(%.3f,%.3f,%.3f)" % (
                max(p.x for p in bb) - min(p.x for p in bb),
                max(p.y for p in bb) - min(p.y for p in bb),
                max(p.z for p in bb) - min(p.z for p in bb),
                (max(p.x for p in bb) + min(p.x for p in bb)) * .5,
                (max(p.y for p in bb) + min(p.y for p in bb)) * .5,
                (max(p.z for p in bb) + min(p.z for p in bb)) * .5)
        except Exception:
            dim = ""
        mats = [sl.material.name if sl.material else None for sl in ob.material_slots] if ob.type == 'MESH' else []
        out.append("%s  %-40s %-9s v=%-7s %s mats=%s" % ("  " * (d + 1), ob.name, ob.type, nv, dim, mats))
        if ob.type == 'ARMATURE':
            out.append("%s      BONES: %s" % ("  " * (d + 1), [b.name for b in ob.data.bones][:80]))
    for ch in sorted(c.children, key=lambda x: x.name):
        walk(ch, d + 1)

if o.instance_collection:
    walk(o.instance_collection)

out.append("")
out.append("=== all collections in file ===")
for c in sorted(bpy.data.collections, key=lambda x: x.name):
    out.append("  %-46s objs=%-4d ch=%-3d lib=%s" %
               (c.name, len(c.objects), len(c.children),
                c.library.filepath if c.library else "-"))

out.append("")
out.append("=== libraries ===")
for L in bpy.data.libraries:
    out.append("  %s  (%d users)" % (L.filepath, L.users))

print("\n".join(out))
