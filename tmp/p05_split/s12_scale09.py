import bpy, json, math
from mathutils import Vector, Matrix
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
cam = SC.camera; lens=cam.data.lens; sw=cam.data.sensor_width
rx, ry = SC.render.resolution_x, SC.render.resolution_y
PIVOT = Vector((0.05,-0.90,0.05))
SCALE     = 0.9                    # requested shrink
K2        = 1.0/SCALE              # extra dolly-back
CUR_L, CUR_R, SHIFT_CUR = 0.434, 0.970, -0.15   # measured on c8/c9 renders
TARGET_L  = 0.425                  # new left edge -> "a little further left"
rep = {}

# --- shift needed after the shrink ---
xl = (CUR_L - 0.5 + SHIFT_CUR) * SCALE
xr = (CUR_R - 0.5 + SHIFT_CUR) * SCALE
SHIFT_NEW = 0.5 + xl - TARGET_L
rep["predicted_span"] = [round(TARGET_L,4), round(0.5 - SHIFT_NEW + xr, 4)]
rep["shift_x"] = round(SHIFT_NEW, 4)

# --- dolly the camera path back about the pivot (keys + handles) ---
act = cam.animation_data.action
for fc in act.fcurves:
    if fc.data_path != "location": continue
    p = PIVOT[fc.array_index]
    for kp in fc.keyframe_points:
        kp.co[1]           = p + (kp.co[1]           - p) * K2
        kp.handle_left[1]  = p + (kp.handle_left[1]  - p) * K2
        kp.handle_right[1] = p + (kp.handle_right[1] - p) * K2
    fc.update()
cam.data.shift_x = SHIFT_NEW
rep["cam_keys"] = {fc.array_index: [round(k.co[1],4) for k in fc.keyframe_points]
                   for fc in act.fcurves if fc.data_path=="location"}

# --- person: same 0.9x shrink, nudged left so the body still bleeds off frame ---
def ev(o,p,i,f):
    for fc in o.animation_data.action.fcurves:
        if fc.data_path==p and fc.array_index==i: return fc.evaluate(f)
F=1620
loc  = Vector([ev(cam,"location",i,F) for i in range(3)])
th   = ev(bpy.data.objects["X5_CAM_ORBIT"], "rotation_euler", 2, F) or 0.0
cpos = PIVOT + Matrix.Rotation(th,3,'Z') @ (loc - PIVOT)
tpos = Vector([ev(bpy.data.objects["X5_CAM_TARGET"],"location",i,F) for i in range(3)])
fwd=(tpos-cpos).normalized(); camZ=-fwd
camX=Vector((0,0,1)).cross(camZ).normalized(); camY=camZ.cross(camX).normalized()
D, NDC_X, NDC_Y = 10.0*K2, -0.72, 0.05
X=(NDC_X/2.0+SHIFT_NEW)*sw*D/lens; Y=(NDC_Y/2.0*(ry/rx))*sw*D/lens
tw = cpos+fwd*D+camX*X+camY*Y
p_local=Vector((0.0495,-0.7115,0.099))
theta=math.atan2((cpos-tw).y,(cpos-tw).x)-math.pi/2.0
Rz=Matrix.Rotation(theta,4,'Z')
bpy.data.objects["P05_WORN_ROOT"].matrix_basis = Matrix.Translation(tw-(Rz.to_3x3()@p_local))@Rz
for nm,r,u,t in (("LGT_P05W_Key",-2.6,2.1,2.0),("LGT_P05W_Rim_R",2.4,1.4,-2.2),
                 ("LGT_P05W_Device",-0.9,0.5,1.6),("LGT_P05W_Fill",-1.6,-1.6,1.4),
                 ("LGT_P05W_Skin_L",-3.0,-0.4,-0.6)):
    bpy.data.objects[nm].matrix_basis = Matrix.Translation(tw+camX*r*K2+camY*u*K2+(-fwd)*t*K2)
rep["cam_pos_1620"]=[round(v,3) for v in cpos]
rep["person_dist"]=round(D,3); rep["person_world"]=[round(v,3) for v in tw]

# --- gobo back to sit between product and person ---
DEPTH, WIPE, SOFT, PLANE_CX = 9.3, 0.02, 0.08, 2.4
gob=bpy.data.objects["P05_GOBO_RIGHT"]
gob.matrix_basis = Matrix.Translation(Vector((PLANE_CX,0.0,-DEPTH)))
half_w=0.5*sw*DEPTH/lens; centre=SHIFT_NEW*sw*DEPTH/lens
wipe_x=centre+WIPE*half_w; soft=SOFT*half_w
mr=bpy.data.materials["MAT_P05_GOBO"].node_tree.nodes["EDGE"]
mr.inputs[1].default_value=(wipe_x-PLANE_CX)-soft
mr.inputs[2].default_value=(wipe_x-PLANE_CX)+soft
rep["gobo_depth"]=DEPTH
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
