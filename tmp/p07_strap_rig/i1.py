import bpy, math
from mathutils import Vector
out = []

out.append("file: %s" % bpy.data.filepath)
out.append("scenes: %s" % [s.name for s in bpy.data.scenes])

# ---- find every scene and its object count ---------------------------------
for s in bpy.data.scenes:
    out.append("  %-34s objs=%-4d fps=%s range=%d-%d cam=%s"
               % (s.name, len(s.objects), s.render.fps, s.frame_start, s.frame_end,
                  s.camera.name if s.camera else None))

# ---- hunt for anything body / hand / human ---------------------------------
KEY = ("body", "human", "man", "woman", "person", "hand", "arm", "finger",
       "torso", "mannequin", "figure", "model_", "skin")
out.append("")
out.append("=== candidate body/hand objects (whole file) ===")
for o in bpy.data.objects:
    ln = o.name.lower()
    if any(k in ln for k in KEY):
        scn = [s.name for s in bpy.data.scenes if o.name in s.objects]
        try:
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            dx = max(p.x for p in bb) - min(p.x for p in bb)
            dy = max(p.y for p in bb) - min(p.y for p in bb)
            dz = max(p.z for p in bb) - min(p.z for p in bb)
            ctr = ((max(p.x for p in bb) + min(p.x for p in bb)) * .5,
                   (max(p.y for p in bb) + min(p.y for p in bb)) * .5,
                   (max(p.z for p in bb) + min(p.z for p in bb)) * .5)
            dim = "dim=(%.3f,%.3f,%.3f) ctr=(%.3f,%.3f,%.3f)" % (dx, dy, dz, ctr[0], ctr[1], ctr[2])
        except Exception as e:
            dim = "dim=? %s" % e
        nv = len(o.data.vertices) if o.type == 'MESH' else '-'
        out.append("  %-40s %-9s v=%-7s hide=%s scenes=%s %s"
                   % (o.name, o.type, nv, o.hide_render, scn, dim))

# ---- armatures anywhere ----------------------------------------------------
out.append("")
out.append("=== armatures ===")
for o in bpy.data.objects:
    if o.type == 'ARMATURE':
        scn = [s.name for s in bpy.data.scenes if o.name in s.objects]
        out.append("  %-40s bones=%-4d scenes=%s" % (o.name, len(o.data.bones), scn))

# ---- scene 01 full object list --------------------------------------------
s1 = None
for s in bpy.data.scenes:
    if s.name.startswith("01") or "P01" in s.name:
        s1 = s
        break
if s1:
    out.append("")
    out.append("=== %s full object list ===" % s1.name)
    for o in sorted(s1.objects, key=lambda x: x.name):
        nv = len(o.data.vertices) if o.type == 'MESH' else '-'
        out.append("  %-46s %-9s v=%-7s hr=%s" % (o.name, o.type, nv, o.hide_render))

print("\n".join(out))
