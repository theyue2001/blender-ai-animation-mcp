import bpy, json
L=[]
L.append("FILE: %s" % bpy.data.filepath)
L.append("SCENES: %s" % [ (s.name, s.frame_start, s.frame_end) for s in bpy.data.scenes ])
L.append("WINDOW SCENE: %s" % bpy.context.window.scene.name)
cands=[]
for o in bpy.data.objects:
    n=o.name
    if n in ("64.002","65.002","58.002") or "STRAP" in n.upper() or "BUCKLE" in n.upper():
        cands.append(o)
L.append("--- CANDIDATES ---")
for o in cands:
    d=o.data
    L.append("%s type=%s mesh=%s verts=%s users=%s parent=%s scenes=%s hide_r=%s dim=%s loc=%s" % (
        o.name, o.type, getattr(d,'name',None), len(d.vertices) if o.type=='MESH' else '-',
        d.users if d else '-', o.parent.name if o.parent else None,
        [s.name for s in o.users_scene], o.hide_render,
        tuple(round(v,4) for v in o.dimensions), tuple(round(v,4) for v in o.location)))
    L.append("    colls=%s vgroups=%s mods=%s mats=%s" % ([c.name for c in o.users_collection],
        [g.name for g in o.vertex_groups], [(m.name,m.type) for m in o.modifiers],
        [(s.link, s.material.name if s.material else None) for s in o.material_slots]))
print("\n".join(L))
