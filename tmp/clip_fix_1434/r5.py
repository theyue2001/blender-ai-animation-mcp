import bpy, os
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev_scene = win.scene
r = sc.render
P = dict(e=r.engine, pct=r.resolution_percentage, fp=r.filepath, ub=r.use_border, uc=r.use_crop_to_border)
try:
    win.scene = sc; sc.frame_set(1434)
    r.engine='BLENDER_EEVEE_NEXT'; r.resolution_percentage=100
    r.use_border=False; r.use_crop_to_border=False
    r.filepath = os.path.join(OUT, "after_1920.png")
    bpy.ops.render.render(write_still=True)
    msg="ok"
finally:
    r.engine=P['e']; r.resolution_percentage=P['pct']; r.filepath=P['fp']
    r.use_border=P['ub']; r.use_crop_to_border=P['uc']
    win.scene = prev_scene
print(msg)
