import bpy, json, math
from mathutils import Vector, Matrix
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
cam = SC.camera
rep = {"fps": SC.render.fps / SC.render.fps_base,
       "range": [SC.frame_start, SC.frame_end],
       "frames": SC.frame_end - SC.frame_start + 1}
rep["seconds"] = round(rep["frames"] / rep["fps"], 2)
rep["markers"] = [[m.frame, m.name, round((m.frame-SC.frame_start)/rep["fps"],1)]
                  for m in sorted(SC.timeline_markers, key=lambda m: m.frame)]

PIVOT = Vector((0.05, -0.90, 0.05))
F0, F1 = 1080, 1560           # orbit start -> settle (2 s before the 1620 climax)
TARGET_AZ = math.radians(45.0)

def ev(o,p,i,f):
    for fc in o.animation_data.action.fcurves:
        if fc.data_path==p and fc.array_index==i: return fc.evaluate(f)
c0 = Vector([ev(cam,"location",i,F0) for i in range(3)])
base_az = math.atan2(c0.y - PIVOT.y, c0.x - PIVOT.x)
delta = TARGET_AZ - base_az
rep["base_az_deg"] = round(math.degrees(base_az),2)
rep["orbit_delta_deg"] = round(math.degrees(delta),2)

orb = bpy.data.objects.get("X5_CAM_ORBIT")
if orb is None:
    orb = bpy.data.objects.new("X5_CAM_ORBIT", None)
    orb.empty_display_type='SINGLE_ARROW'; orb.empty_display_size=0.8
    bpy.data.collections["P05_XRAY_RIG"].objects.link(orb)
orb.matrix_basis = Matrix.Translation(PIVOT)
# parent the camera so its animated location orbits about PIVOT
cam.parent = orb
cam.matrix_parent_inverse = Matrix.Translation(-PIVOT)

if orb.animation_data is None: orb.animation_data_create()
if orb.animation_data.action is None:
    orb.animation_data.action = bpy.data.actions.new("ACT_P05_CAM_ORBIT")
act = orb.animation_data.action
for fc in list(act.fcurves):
    if fc.data_path == "rotation_euler": act.fcurves.remove(fc)
fc = act.fcurves.new("rotation_euler", index=2)
for f, v in ((F0, delta), (F1, 0.0)):
    kp = fc.keyframe_points.insert(f, v)
    kp.interpolation = 'BEZIER'
    kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
fc.update()
rep["orbit_keys"] = [[F0, round(math.degrees(delta),2)], [F1, 0.0]]
rep["orbit_seconds"] = round((F1-F0)/rep["fps"], 1)
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
