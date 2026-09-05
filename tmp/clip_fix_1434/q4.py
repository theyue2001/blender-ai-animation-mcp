import bpy
from mathutils import Vector
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
try:
    win.scene = sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    L=[]
    L.append("%-30s %8s %8s  %-28s  %s" % ("OBJ","verts","polys","mats","world bbox min/max"))
    for o in sorted([o for o in sc.objects if o.type=='MESH'], key=lambda x:x.name):
        oe = o.evaluated_get(dg)
        me = oe.data
        bb = [oe.matrix_world @ Vector(c) for c in oe.bound_box]
        mn = Vector((min(p.x for p in bb), min(p.y for p in bb), min(p.z for p in bb)))
        mx = Vector((max(p.x for p in bb), max(p.y for p in bb), max(p.z for p in bb)))
        mats = ",".join(sorted({s.material.name for s in o.material_slots if s.material}))
        L.append("%-30s %8d %8d  %-28s  (%.3f,%.3f,%.3f)-(%.3f,%.3f,%.3f)" % (
            o.name, len(me.vertices), len(me.polygons), mats[:28], mn.x,mn.y,mn.z, mx.x,mx.y,mx.z))
    print("\n".join(L))
finally:
    win.scene = prev
