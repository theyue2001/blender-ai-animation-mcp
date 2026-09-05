import bpy, os, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene
prev_frames = {s.name: s.frame_current for s in bpy.data.scenes}
bpy.context.window.scene = SC
r = SC.render
sav = (r.engine, r.resolution_percentage, r.filepath, r.image_settings.file_format, SC.camera.data.shift_x)
out = []
try:
    SC.camera.data.shift_x = -0.23
    r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_percentage = 50
    r.image_settings.file_format = 'PNG'
    SC.eevee.taa_render_samples = 16
    for f in (1620,):
        SC.frame_set(f)
        r.filepath = "D:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p05_split/eevee3_%d.png" % f
        bpy.ops.render.render(write_still=True)
        out.append([f, os.path.exists(bpy.path.abspath(r.filepath))])
finally:
    r.engine, r.resolution_percentage, r.filepath, r.image_settings.file_format, SC.camera.data.shift_x = sav
    for s in bpy.data.scenes:
        if s.name in prev_frames: s.frame_set(prev_frames[s.name])
    bpy.context.window.scene = prev
print(json.dumps(out))
