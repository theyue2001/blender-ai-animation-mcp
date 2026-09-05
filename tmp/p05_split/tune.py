import bpy, json, math, sys, os
from mathutils import Vector, Matrix
P = json.loads(os.environ.get("TUNE", "{}"))
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
cam = SC.camera; lens=cam.data.lens; sw=cam.data.sensor_width
rx, ry = SC.render.resolution_x, SC.render.resolution_y
SHIFT_X = P.get("shift_x", -0.23); D=P.get("d",10.0)
NDC_X=P.get("ndc_x",-0.68); NDC_Y=P.get("ndc_y",0.05)
WIPE=P.get("wipe",0.02); SOFT=P.get("soft",0.08); DEPTH=P.get("depth",7.5)
F=1620
def ev(o,p,i,f):
    for fc in o.animation_data.action.fcurves:
        if fc.data_path==p and fc.array_index==i: return fc.evaluate(f)
cpos=Vector([ev(cam,"location",i,F) for i in range(3)])
tpos=Vector([ev(bpy.data.objects["X5_CAM_TARGET"],"location",i,F) for i in range(3)])
fwd=(tpos-cpos).normalized(); camZ=-fwd
camX=Vector((0,0,1)).cross(camZ).normalized(); camY=camZ.cross(camX).normalized()
X=(NDC_X/2.0+SHIFT_X)*sw*D/lens; Y=(NDC_Y/2.0*(ry/rx))*sw*D/lens
tw = cpos+fwd*D+camX*X+camY*Y
p_local=Vector((0.0495,-0.7115,0.099))
theta=math.atan2((cpos-tw).y,(cpos-tw).x)-math.pi/2.0
Rz=Matrix.Rotation(theta,4,'Z')
root=bpy.data.objects["P05_WORN_ROOT"]
root.matrix_basis=Matrix.Translation(tw-(Rz.to_3x3()@p_local))@Rz
LP = P.get("lights", {})
for nm,r,u,t,en in (("LGT_P05W_Key",-2.6,2.1,2.0,None),("LGT_P05W_Rim_R",2.4,1.4,-2.2,None),
                    ("LGT_P05W_Device",-0.9,0.5,1.6,None),("LGT_P05W_Fill",-1.6,-1.6,1.4,None),
                    ("LGT_P05W_Skin_L",-3.0,-0.4,-0.6,None)):
    o=bpy.data.objects[nm]
    spec = LP.get(nm, {})
    r,u,t = spec.get("pos",[r,u,t])
    o.matrix_basis=Matrix.Translation(tw+camX*r+camY*u+(-fwd)*t)
    if "energy" in spec: o.data.energy=spec["energy"]
    if "size" in spec: o.data.size=spec["size"]
    if "color" in spec: o.data.color=spec["color"]
# gobo
gob=bpy.data.objects["P05_GOBO_RIGHT"]; PLANE_CX=2.4
gob.matrix_basis=Matrix.Translation(Vector((PLANE_CX,0.0,-DEPTH)))
half_w=0.5*sw*DEPTH/lens; centre_x=SHIFT_X*sw*DEPTH/lens
wipe_x=centre_x+WIPE*half_w; soft=SOFT*half_w
mr=bpy.data.materials["MAT_P05_GOBO"].node_tree.nodes["EDGE"]
mr.inputs[1].default_value=(wipe_x-PLANE_CX)-soft
mr.inputs[2].default_value=(wipe_x-PLANE_CX)+soft
cam.data.shift_x = SHIFT_X
bpy.ops.wm.save_mainfile()
print(json.dumps({"person":[round(v,3) for v in tw],"theta":round(math.degrees(theta),2),
                  "wipe_cam_x":round(wipe_x,3),"params":P}, ensure_ascii=False))
bpy.context.window.scene=prev
