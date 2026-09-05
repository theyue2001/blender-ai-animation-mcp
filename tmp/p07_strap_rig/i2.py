import bpy
out = []
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]

out.append("=== %s objects ===" % SN)
for o in sorted(sc.objects, key=lambda x: x.name):
    nv = len(o.data.vertices) if o.type == 'MESH' else '-'
    mats = []
    if o.type == 'MESH':
        for sl in o.material_slots:
            mats.append("%s[%s]" % (sl.material.name if sl.material else None, sl.link))
    out.append("  %-42s %-9s v=%-7s hr=%s %s" % (o.name, o.type, nv, o.hide_render, ",".join(mats)))

out.append("")
out.append("=== strap material node graphs ===")
for mn in ("MAT_P07_STRAP_UPPER", "MAT_P07_STRAP_LOWER"):
    m = bpy.data.materials.get(mn)
    if not m:
        out.append("  %s : MISSING" % mn)
        continue
    out.append("  --- %s users=%d nodes=%d" % (mn, m.users, len(m.node_tree.nodes)))
    for n in m.node_tree.nodes:
        out.append("      %-28s %-24s loc=(%.0f,%.0f)" % (n.name, n.type, n.location.x, n.location.y))
        if n.type == 'BSDF_PRINCIPLED':
            for k in ("Base Color", "Metallic", "Roughness", "IOR", "Alpha",
                      "Specular IOR Level", "Sheen Weight", "Sheen Roughness", "Sheen Tint",
                      "Coat Weight", "Coat Roughness", "Anisotropic", "Anisotropic Rotation"):
                if k in n.inputs:
                    v = n.inputs[k].default_value
                    try:
                        v = tuple(round(x, 4) for x in v)
                    except TypeError:
                        v = round(v, 4)
                    out.append("        %-22s = %s  linked=%s" % (k, v, n.inputs[k].is_linked))
    for l in m.node_tree.links:
        out.append("      LINK %s.%s -> %s.%s" % (l.from_node.name, l.from_socket.name,
                                                  l.to_node.name, l.to_socket.name))

out.append("")
out.append("=== strap mesh UVs / size ===")
for on in ("P07_STRAP_UPPER", "P07_STRAP_LOWER"):
    o = bpy.data.objects.get(on)
    if not o:
        out.append("  %s MISSING" % on)
        continue
    me = o.data
    out.append("  %-20s v=%-7d poly=%-7d uv_layers=%s"
               % (on, len(me.vertices), len(me.polygons), [u.name for u in me.uv_layers]))
    if me.uv_layers:
        uv = me.uv_layers.active.data
        us = [d.uv[0] for d in uv]; vs = [d.uv[1] for d in uv]
        out.append("      UV range u %.3f..%.3f  v %.3f..%.3f" % (min(us), max(us), min(vs), max(vs)))
    out.append("      modifiers: %s" % [(m.name, m.type) for m in o.modifiers])
    out.append("      vgroups: %d" % len(o.vertex_groups))

out.append("")
out.append("=== render settings ===")
out.append("  engine=%s  res=%dx%d @%d%%  samples=%s"
           % (sc.render.engine, sc.render.resolution_x, sc.render.resolution_y,
              sc.render.resolution_percentage,
              getattr(sc.cycles, 'samples', None) if hasattr(sc, 'cycles') else None))
out.append("  view_transform=%s look=%s" % (sc.view_settings.view_transform, sc.view_settings.look))

print("\n".join(out))
