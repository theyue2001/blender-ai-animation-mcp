import bpy, json
out={"scenes":{}}
for s in bpy.data.scenes:
    out["scenes"][s.name]={"fps": s.render.fps/s.render.fps_base, "range":[s.frame_start,s.frame_end],
        "cur": s.frame_current,
        "markers": [[m.frame, m.name] for m in sorted(s.timeline_markers, key=lambda m:m.frame)]}
SC=bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
cam=SC.camera
out["cam_loc_keys"]=[round(k.co[0]) for k in cam.animation_data.action.fcurves[0].keyframe_points]
orb=bpy.data.objects.get("X5_CAM_ORBIT")
out["orbit_keys"]=[[round(k.co[0]),round(k.co[1],4)] for k in orb.animation_data.action.fcurves[0].keyframe_points] if orb and orb.animation_data else None
ms=bpy.data.objects["X5_MOTOR_SPIN"]
kp=ms.animation_data.action.fcurves.find("rotation_euler",index=2).keyframe_points
out["motor_keys"]={"n":len(kp),"first":round(kp[0].co[0]),"last":round(kp[-1].co[0])}
ctrl=bpy.data.objects["X5_CTRL"]
out["ctrl_xray_keys"]=[[round(k.co[0]),round(k.co[1],3)] for k in ctrl.animation_data.action.fcurves[0].keyframe_points]
out["gobo_present"]="P05_GOBO_RIGHT" in bpy.data.objects
out["shift_x"]=round(cam.data.shift_x,4)
out["worn_root_loc"]=[round(v,3) for v in bpy.data.objects["P05_WORN_ROOT"].location]
print(json.dumps(out, ensure_ascii=False, indent=1))
