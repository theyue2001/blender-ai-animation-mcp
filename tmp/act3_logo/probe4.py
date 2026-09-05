import bpy
L=[]
sc = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
L.append("frame_current=%d  engine=%s  res=%dx%d @%d%%" % (sc.frame_current, sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage))
L.append("=== WRN_* hide keys ===")
nokey=[]
for o in sorted(sc.objects, key=lambda x:x.name):
    if not o.name.startswith("WRN_"): continue
    ad=o.animation_data
    rows=[]
    if ad and ad.action:
        for fc in ad.action.fcurves:
            if fc.data_path in ("hide_render","hide_viewport"):
                rows.append("%s=%s" % (fc.data_path[5:], [(int(k.co[0]),round(k.co[1],2)) for k in fc.keyframe_points]))
    if rows: L.append("  %-34s %s" % (o.name, "  ".join(rows)))
    else: nokey.append(o.name)
L.append("  NO HIDE KEYS (%d): %s" % (len(nokey), ", ".join(nokey)))
L.append("")
L.append("=== collection exclusion / hide in view layer ===")
vl = sc.view_layers[0]
def walk(lc, d=0):
    L.append("  "*d + "%-30s exclude=%s hide_vp=%s coll.hide_render=%s coll.hide_viewport=%s" % (lc.name, lc.exclude, lc.hide_viewport, lc.collection.hide_render, lc.collection.hide_viewport))
    for c in lc.children: walk(c, d+1)
walk(vl.layer_collection)
print("\n".join(L))
