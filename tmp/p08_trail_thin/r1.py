import bpy, os, json
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
win=bpy.context.window; prev_scene=win.scene
prev={"eng":sc.render.engine,"rx":sc.render.resolution_x,"ry":sc.render.resolution_y,
      "pct":sc.render.resolution_percentage,"fp":sc.render.filepath,"ff":sc.render.image_settings.file_format,
      "frame":sc.frame_current,"cam":sc.camera.name if sc.camera else None}
mk={m.name:(m.frame,m.camera.name if m.camera else None) for m in sc.timeline_markers}
outdir=r"d:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p08_trail_thin/qa"
outdir=bpy.path.abspath("//")  # placeholder
OUT=r"D:/\u63a5\u6848"
print(json.dumps({"prev":prev,"markers":mk,"engine":sc.render.engine}))
