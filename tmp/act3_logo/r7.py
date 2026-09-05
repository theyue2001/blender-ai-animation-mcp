import bpy
OUT = r"D:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\act3_logo"
def render(scname, frame, tag, pct=50, samples=48):
    sc = bpy.data.scenes[scname]; prev = bpy.context.window.scene; pfr = sc.frame_current
    pe,pp = sc.render.engine, sc.render.resolution_percentage
    pb,pc,pf = sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath
    pss = sc.cycles.samples
    try:
        bpy.context.window.scene = sc; sc.frame_set(frame)
        sc.render.engine='CYCLES'; sc.render.resolution_percentage=pct
        sc.render.use_border=False; sc.render.use_crop_to_border=False
        sc.cycles.samples=samples
        p = OUT+"\\"+tag+".png"; sc.render.filepath=p
        bpy.ops.render.render(write_still=True); return p
    finally:
        sc.render.engine, sc.render.resolution_percentage = pe,pp
        sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath = pb,pc,pf
        sc.cycles.samples = pss; sc.frame_set(pfr); bpy.context.window.scene = prev
L=[render("03_SCN_P05_XRAY_MECHANISM", 900, "wide_900"),
   render("03_SCN_P05_XRAY_MECHANISM", 1340, "wide_1340")]
# integrity check: nothing else uses these materials
for mn in ("MAT_P05W_Logo","MAT_P05_Logo"):
    m=bpy.data.materials[mn]
    users=[o.name for o in bpy.data.objects for s in o.material_slots if s.material is m]
    L.append("%s users=%d objs=%s" % (mn, m.users, users))
L.append("file=%s  dirty=%s" % (bpy.data.filepath, bpy.data.is_dirty))
print("\n".join(L))
