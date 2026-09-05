import bpy, os
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev_scene = win.scene
r = sc.render
P = dict(e=r.engine, pct=r.resolution_percentage, fp=r.filepath, ub=r.use_border, uc=r.use_crop_to_border,
         bx0=r.border_min_x, bx1=r.border_max_x, by0=r.border_min_y, by1=r.border_max_y, f=sc.frame_current)
try:
    win.scene = sc; sc.frame_set(1434)
    r.engine='BLENDER_EEVEE_NEXT'; r.resolution_percentage=100
    r.use_border=True; r.use_crop_to_border=True
    r.border_min_x, r.border_max_x = 0.6135, 0.9146
    r.border_min_y, r.border_max_y = 0.4630, 0.9972
    r.filepath = os.path.join(OUT, "cmp_UR.png")
    bpy.ops.render.render(write_still=True)
    msg="ok"
finally:
    r.engine=P['e']; r.resolution_percentage=P['pct']; r.filepath=P['fp']
    r.use_border=P['ub']; r.use_crop_to_border=P['uc']
    r.border_min_x=P['bx0']; r.border_max_x=P['bx1']; r.border_min_y=P['by0']; r.border_max_y=P['by1']
    win.scene = prev_scene
print(msg)
