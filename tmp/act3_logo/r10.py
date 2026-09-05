import bpy
OUT = "D:/接案/26_0825_紅犀牛3D動畫/VScode/tmp/act3_logo"
def render(scname, frame, tag, bx=None, by=None, pct=100, samples=64):
    sc = bpy.data.scenes[scname]; prev = bpy.context.window.scene; pfr = sc.frame_current
    pe,pp = sc.render.engine, sc.render.resolution_percentage
    pb,pc,pf = sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath
    pss = sc.cycles.samples
    try:
        bpy.context.window.scene = sc; sc.frame_set(frame)
        sc.render.engine='CYCLES'; sc.render.resolution_percentage=pct
        crop = bx is not None
        sc.render.use_border=crop; sc.render.use_crop_to_border=crop
        if crop:
            sc.render.border_min_x,sc.render.border_max_x = bx
            sc.render.border_min_y,sc.render.border_max_y = by
        sc.cycles.samples=samples
        sc.render.filepath = OUT + "/" + tag + ".png"
        bpy.ops.render.render(write_still=True)
        return tag
    finally:
        sc.render.engine, sc.render.resolution_percentage = pe,pp
        sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath = pb,pc,pf
        sc.cycles.samples = pss; sc.frame_set(pfr); bpy.context.window.scene = prev
print(render("01_SCN_OPENING_P01_P03", 340, "s01_full_340", pct=50, samples=48))
print(render("01_SCN_OPENING_P01_P03", 340, "s01_dev_340", (0.33,0.67),(0.10,0.75), samples=96))
