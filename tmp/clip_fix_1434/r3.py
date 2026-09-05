import bpy, os
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev_scene = win.scene
r = sc.render
P = dict(e=r.engine, pct=r.resolution_percentage, fp=r.filepath, ub=r.use_border, uc=r.use_crop_to_border,
         b=(r.border_min_x,r.border_max_x,r.border_min_y,r.border_max_y))
regions = {
 "zoomA_armjoin": (0.547, 0.781, 0.5185, 0.7685),
 "zoomB_rightcorner": (0.729, 0.9375, 0.3518, 0.7222),
}
try:
    win.scene = sc; sc.frame_set(1434)
    r.engine='BLENDER_EEVEE_NEXT'; r.resolution_percentage=200
    r.use_border=True; r.use_crop_to_border=True
    for k,(x0,x1,y0,y1) in regions.items():
        r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = x0,x1,y0,y1
        r.filepath = os.path.join(OUT, k + ".png")
        bpy.ops.render.render(write_still=True)
    msg="ok"
finally:
    r.engine=P['e']; r.resolution_percentage=P['pct']; r.filepath=P['fp']
    r.use_border=P['ub']; r.use_crop_to_border=P['uc']
    r.border_min_x,r.border_max_x,r.border_min_y,r.border_max_y = P['b']
    win.scene = prev_scene
print(msg)
