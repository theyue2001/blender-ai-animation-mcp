import bpy, os
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window
prev_scene = win.scene
prev = dict(engine=sc.render.engine, rx=sc.render.resolution_x, ry=sc.render.resolution_y,
            pct=sc.render.resolution_percentage, fp=sc.render.filepath, frame=sc.frame_current)
try:
    win.scene = sc
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 50
    sc.frame_set(1434)
    sc.render.filepath = os.path.join(OUT, "look_1434_full.png")
    bpy.ops.render.render(write_still=True)
    msg = "rendered " + sc.render.filepath
finally:
    sc.render.engine = prev['engine']
    sc.render.resolution_x = prev['rx']; sc.render.resolution_y = prev['ry']
    sc.render.resolution_percentage = prev['pct']; sc.render.filepath = prev['fp']
    win.scene = prev_scene
print(msg)
