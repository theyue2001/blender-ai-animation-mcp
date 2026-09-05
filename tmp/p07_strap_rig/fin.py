import bpy
sc=bpy.data.scenes["05_SCN_P07_STRAP_RIG"]
print("loaded file: %s"%bpy.data.filepath)
print("scene range %d-%d fps=%d camera=%s"%(sc.frame_start,sc.frame_end,sc.render.fps,sc.camera.name))
for o in sc.objects:
    ad=o.animation_data
    if ad and ad.action:
        f=[k.co[0] for fc in ad.action.fcurves for k in fc.keyframe_points]
        print("  %-24s %-26s %d keys  %.0f..%.0f"%(o.name,ad.action.name,len(f),min(f),max(f)))
    if o.type=='CAMERA' and o.data.animation_data and o.data.animation_data.action:
        f=[k.co[0] for fc in o.data.animation_data.action.fcurves for k in fc.keyframe_points]
        print("  %-24s (lens/dof) %d keys %.0f..%.0f"%(o.name,len(f),min(f),max(f)))
print("actions kept: %s"%[a.name for a in bpy.data.actions if a.name.startswith("P07_")])
bpy.ops.wm.save_mainfile()
print("saved: %s"%bpy.data.filepath)
