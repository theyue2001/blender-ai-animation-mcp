import bpy, time
out = []
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]

# ---- isolation audit: nothing outside the new scene may have been touched ----
for nm in ("P01_STRAP_UPPER", "P01_STRAP_LOWER", "64.002", "65.002", "58.002",
           "59.002", "60.002", "63.002", "64.005"):
    o = bpy.data.objects[nm]
    out.append("%-16s mods=%d vgroups=%d action=%s slots=%s scenes=%s" %
               (nm, len(o.modifiers), len(o.vertex_groups),
                bool(o.animation_data and o.animation_data.action),
                [s.link for s in o.material_slots],
                [s.name for s in o.users_scene]))
for mn in ("Rubber #4", "Rubber #5"):
    m = bpy.data.materials[mn]
    out.append("%-10s ignition_nodes=%d node_anim=%s users=%d" %
               (mn, len([n for n in m.node_tree.nodes if "IGNITION" in n.name]),
                bool(m.node_tree.animation_data and m.node_tree.animation_data.action), m.users))
leak = [o.name for o in bpy.data.objects
        if o.name.startswith(("P07_", "P07R_", "NITE_", "CRV_", "WGT_P07"))
        and any(s.name != SN for s in o.users_scene)]
out.append("P07 objects leaking into other scenes: %s" % (leak or "none"))
out.append("scene object count: %d ; scenes in file: %s" %
           (len(sc.objects), [s.name for s in bpy.data.scenes]))

# ---- rig inventory ----
for tag in ("StrapUpper", "StrapLower"):
    ao = bpy.data.objects["NITE_%s_Armature" % tag]
    ob = bpy.data.objects["P07_%s" % ("STRAP_UPPER" if tag == "StrapUpper" else "STRAP_LOWER")]
    cu = bpy.data.objects["CRV_%s_Path" % tag]
    out.append("%s: %d bones (%d DEF / %d CP / %d CTRL) | curve %d pts %d hooks | mesh %d verts, %d vgroups, mods=%s"
               % (ao.name, len(ao.data.bones),
                  sum(1 for b in ao.data.bones if b.use_deform),
                  sum(1 for b in ao.data.bones if "_CP_" in b.name),
                  sum(1 for b in ao.data.bones if b.name.endswith("_CTRL")),
                  len(cu.data.splines[0].bezier_points),
                  len([m for m in cu.modifiers if m.type == 'HOOK']),
                  len(ob.data.vertices), len(ob.vertex_groups),
                  [(m.name, m.type) for m in ob.modifiers]))

t0 = time.time()
bpy.ops.wm.save_mainfile()
out.append("SAVED %s in %.1fs" % (bpy.data.filepath, time.time() - t0))
print("\n".join(out))
