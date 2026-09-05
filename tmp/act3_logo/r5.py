import bpy
OUT = r"D:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\act3_logo"
def render_crop(scname, frame, bx, by, tag, samples=64, crop=True):
    sc = bpy.data.scenes[scname]
    prev = bpy.context.window.scene
    pfr = sc.frame_current
    pe, pp = sc.render.engine, sc.render.resolution_percentage
    pb, pc, pf = sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath
    pss = sc.cycles.samples
    try:
        bpy.context.window.scene = sc
        sc.frame_set(frame)
        sc.render.engine='CYCLES'
        sc.render.resolution_percentage = 100 if crop else 50
        sc.render.use_border=crop; sc.render.use_crop_to_border=crop
        if crop:
            sc.render.border_min_x,sc.render.border_max_x = bx
            sc.render.border_min_y,sc.render.border_max_y = by
        sc.cycles.samples=samples
        p = OUT + "\\" + tag + ".png"
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        return p
    finally:
        sc.render.engine, sc.render.resolution_percentage = pe, pp
        sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath = pb, pc, pf
        sc.cycles.samples = pss
        sc.frame_set(pfr)
        bpy.context.window.scene = prev
L=[]
L.append(render_crop("03_SCN_P05_XRAY_MECHANISM", 900, (0.74,0.90), (0.52,0.70), "x5_900"))
L.append(render_crop("03_SCN_P05_XRAY_MECHANISM", 1396, (0.0,0.0), (0.0,0.0), "wide_1396", samples=48, crop=False))
print("\n".join(L))
