import bpy, json, math
from mathutils import Vector, Matrix

SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
cam = SC.camera; lens = cam.data.lens; sw = cam.data.sensor_width
rx, ry = SC.render.resolution_x, SC.render.resolution_y
SHIFT_X = -0.23
DEPTH   = 7.5
WIPE_NDC = 0.10
SOFT_NDC = 0.09

half_w = 0.5*sw*DEPTH/lens
centre_x = SHIFT_X*sw*DEPTH/lens
wipe_cam_x = centre_x + WIPE_NDC*half_w
soft_cam   = SOFT_NDC*half_w

# ---- gobo mesh (8x8 plane facing camera) ----
me = bpy.data.meshes.get("ME_P05_GOBO")
if me is None:
    me = bpy.data.meshes.new("ME_P05_GOBO")
    S=4.0
    me.from_pydata([(-S,-S,0),(S,-S,0),(S,S,0),(-S,S,0)], [], [(0,1,2,3)])
    me.update()
gob = bpy.data.objects.get("P05_GOBO_RIGHT")
if gob is None:
    gob = bpy.data.objects.new("P05_GOBO_RIGHT", me)
    bpy.data.collections["P05_WORN"].objects.link(gob)
PLANE_CX = 2.4
gob.parent = cam
gob.matrix_parent_inverse = Matrix.Identity(4)
gob.matrix_basis = Matrix.Translation(Vector((PLANE_CX, 0.0, -DEPTH)))
for a in ("visible_diffuse","visible_glossy","visible_transmission","visible_volume_scatter","visible_shadow"):
    setattr(gob, a, False)
gob.visible_camera = True

# ---- gobo material: Transparent -> black Emission wipe along object X ----
m = bpy.data.materials.get("MAT_P05_GOBO")
if m is None:
    m = bpy.data.materials.new("MAT_P05_GOBO")
m.use_nodes = True
nt = m.node_tree
nt.nodes.clear()
out  = nt.nodes.new("ShaderNodeOutputMaterial");  out.location=(600,0)
mix  = nt.nodes.new("ShaderNodeMixShader");       mix.location=(400,0);  mix.name="WIPE"
tr   = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.location=(200,120)
em   = nt.nodes.new("ShaderNodeEmission");        em.location=(200,-120); em.inputs[1].default_value=0.0
em.inputs[0].default_value=(0,0,0,1)
tex  = nt.nodes.new("ShaderNodeTexCoord");        tex.location=(-400,0); tex.object = gob
sep  = nt.nodes.new("ShaderNodeSeparateXYZ");     sep.location=(-200,0)
mr   = nt.nodes.new("ShaderNodeMapRange");        mr.location=(0,0); mr.name="EDGE"
lo = (wipe_cam_x - PLANE_CX) - soft_cam
hi = (wipe_cam_x - PLANE_CX) + soft_cam
mr.inputs[1].default_value = lo; mr.inputs[2].default_value = hi
mr.inputs[3].default_value = 0.0; mr.inputs[4].default_value = 1.0
mr.clamp = True; mr.interpolation_type = 'SMOOTHSTEP'
nt.links.new(tex.outputs["Object"], sep.inputs[0])
nt.links.new(sep.outputs["X"], mr.inputs[0])
nt.links.new(mr.outputs[0], mix.inputs[0])
nt.links.new(tr.outputs[0], mix.inputs[1])
nt.links.new(em.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], out.inputs[0])
m.blend_method = 'BLEND'
if not gob.material_slots:
    gob.data.materials.append(None)
gob.material_slots[0].link = 'OBJECT'
gob.material_slots[0].material = m

# ---- nudge the person further left ----
root = bpy.data.objects["P05_WORN_ROOT"]
def ev(obj, path, idx, f):
    for fc in obj.animation_data.action.fcurves:
        if fc.data_path==path and fc.array_index==idx: return fc.evaluate(f)
F=1620
cpos = Vector([ev(cam,"location",i,F) for i in range(3)])
tpos = Vector([ev(bpy.data.objects["X5_CAM_TARGET"],"location",i,F) for i in range(3)])
fwd = (tpos-cpos).normalized(); camZ=-fwd
camX = Vector((0,0,1)).cross(camZ).normalized(); camY = camZ.cross(camX).normalized()
D, NDC_X, NDC_Y = 10.0, -0.68, -0.10
X = (NDC_X/2.0 + SHIFT_X)*sw*D/lens
Y = (NDC_Y/2.0*(ry/rx))*sw*D/lens
target_world = cpos + fwd*D + camX*X + camY*Y
p_local = Vector((0.0495,-0.7115,0.099))
to_cam = cpos - target_world
theta = math.atan2(to_cam.y, to_cam.x) - math.pi/2.0
Rz = Matrix.Rotation(theta,4,'Z')
root.matrix_basis = Matrix.Translation(target_world - (Rz.to_3x3() @ p_local)) @ Rz
for nm, r,u,t in (("LGT_P05W_Key",-2.6,2.1,2.0),("LGT_P05W_Rim_R",2.4,1.4,-2.2),
                  ("LGT_P05W_Device",-0.9,0.5,1.6),("LGT_P05W_Fill",-1.6,-1.6,1.4),
                  ("LGT_P05W_Skin_L",-3.0,-0.4,-0.6)):
    bpy.data.objects[nm].matrix_basis = Matrix.Translation(target_world + camX*r + camY*u + (-fwd)*t)

info = {"wipe_cam_x": round(wipe_cam_x,3), "ramp_local": [round(lo,3), round(hi,3)],
        "person_world":[round(v,3) for v in target_world], "theta_deg": round(math.degrees(theta),2)}
for n in ("SHOT1_HUMAN_Male_0","SHOT1_HUMAN_Underwear_0"):
    mm=bpy.data.materials["MAT_P05W_"+n.replace("SHOT1_","").replace(" ","_")]
    p=mm.node_tree.nodes.get("Principled BSDF")
    info[mm.name]={"base":[round(v,4) for v in p.inputs["Base Color"].default_value],
                   "rough":round(p.inputs["Roughness"].default_value,3),
                   "fade":round(mm.node_tree.nodes["SHOT1_HUMAN_Fade"].inputs[0].default_value,3)}
bpy.ops.wm.save_mainfile()
print(json.dumps(info, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
