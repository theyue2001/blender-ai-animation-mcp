import bpy, json, math
from mathutils import Vector, Matrix
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
cam = SC.camera; lens=cam.data.lens; sw=cam.data.sensor_width
rx, ry = SC.render.resolution_x, SC.render.resolution_y

K       = 1.374      # dolly-back factor -> product 74.2% -> 54% of frame width
SHIFT_X = -0.15      # right-align, ~3% margin off the right edge
PIVOT   = Vector((0.05, -0.90, 0.05))   # X5_CAM_TARGET (moves < 0.08 over the shot)
rep = {}

# --- 1. scale camera path radially about the aim point (keys + handles) ---
act = cam.animation_data.action
before = {}
for fc in act.fcurves:
    if fc.data_path != "location": continue
    p = PIVOT[fc.array_index]
    before[fc.array_index] = [round(k.co[1],4) for k in fc.keyframe_points]
    for kp in fc.keyframe_points:
        kp.co[1]           = p + (kp.co[1]           - p) * K
        kp.handle_left[1]  = p + (kp.handle_left[1]  - p) * K
        kp.handle_right[1] = p + (kp.handle_right[1] - p) * K
    fc.update()
rep["cam_before"] = before
rep["cam_after"] = {fc.array_index: [round(k.co[1],4) for k in fc.keyframe_points]
                    for fc in act.fcurves if fc.data_path=="location"}

# --- 2. shift_x becomes a constant (no more 1620 pan) ---
d = cam.data
if d.animation_data and d.animation_data.action:
    fc = d.animation_data.action.fcurves.find("shift_x")
    if fc: d.animation_data.action.fcurves.remove(fc)
    if not d.animation_data.action.fcurves: d.animation_data_clear()
d.shift_x = SHIFT_X
rep["shift_x"] = SHIFT_X

# --- 3. re-place the person (same on-screen size: same distance from the new camera) ---
def ev(o,p,i,f):
    for fc in o.animation_data.action.fcurves:
        if fc.data_path==p and fc.array_index==i: return fc.evaluate(f)
F=1620
cpos = Vector([ev(cam,"location",i,F) for i in range(3)])
tpos = Vector([ev(bpy.data.objects["X5_CAM_TARGET"],"location",i,F) for i in range(3)])
fwd=(tpos-cpos).normalized(); camZ=-fwd
camX=Vector((0,0,1)).cross(camZ).normalized(); camY=camZ.cross(camX).normalized()
D, NDC_X, NDC_Y = 10.0, -0.68, 0.05
X=(NDC_X/2.0+SHIFT_X)*sw*D/lens; Y=(NDC_Y/2.0*(ry/rx))*sw*D/lens
tw = cpos+fwd*D+camX*X+camY*Y
p_local=Vector((0.0495,-0.7115,0.099))
theta=math.atan2((cpos-tw).y,(cpos-tw).x)-math.pi/2.0
Rz=Matrix.Rotation(theta,4,'Z')
bpy.data.objects["P05_WORN_ROOT"].matrix_basis = Matrix.Translation(tw-(Rz.to_3x3()@p_local))@Rz
for nm,r,u,t in (("LGT_P05W_Key",-2.6,2.1,2.0),("LGT_P05W_Rim_R",2.4,1.4,-2.2),
                 ("LGT_P05W_Device",-0.9,0.5,1.6),("LGT_P05W_Fill",-1.6,-1.6,1.4),
                 ("LGT_P05W_Skin_L",-3.0,-0.4,-0.6)):
    bpy.data.objects[nm].matrix_basis = Matrix.Translation(tw+camX*r+camY*u+(-fwd)*t)
rep["cam_pos_1620"]=[round(v,3) for v in cpos]
rep["cam_dist_to_aim"]=round((cpos-tpos).length,3)
rep["person_world"]=[round(v,3) for v in tw]

# --- 4. gobo now sits between the product and the person ---
DEPTH, WIPE, SOFT, PLANE_CX = 8.4, 0.02, 0.08, 2.4
gob=bpy.data.objects["P05_GOBO_RIGHT"]
gob.matrix_basis = Matrix.Translation(Vector((PLANE_CX,0.0,-DEPTH)))
half_w=0.5*sw*DEPTH/lens; centre_x=SHIFT_X*sw*DEPTH/lens
wipe_x=centre_x+WIPE*half_w; soft=SOFT*half_w
mr=bpy.data.materials["MAT_P05_GOBO"].node_tree.nodes["EDGE"]
mr.inputs[1].default_value=(wipe_x-PLANE_CX)-soft
mr.inputs[2].default_value=(wipe_x-PLANE_CX)+soft
rep["gobo"]={"depth":DEPTH,"wipe_cam_x":round(wipe_x,3)}
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
