import bpy, json, math
from mathutils import Vector, Matrix, Euler

SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene
bpy.context.window.scene = SC
F = 1620

# ---- camera basis at frame 1620, computed from fcurves (no depsgraph) ----
cam = SC.camera
def ev(obj, path, idx, f):
    for fc in obj.animation_data.action.fcurves:
        if fc.data_path == path and fc.array_index == idx:
            return fc.evaluate(f)
    return None
cpos = Vector([ev(cam, "location", i, F) for i in range(3)])
tgt_o = bpy.data.objects["X5_CAM_TARGET"]
tpos = Vector([ev(tgt_o, "location", i, F) for i in range(3)])
fwd = (tpos - cpos).normalized()
camZ = -fwd
camX = Vector((0,0,1)).cross(camZ).normalized()
camY = camZ.cross(camX).normalized()

lens = cam.data.lens; sw = cam.data.sensor_width
rx, ry = SC.render.resolution_x, SC.render.resolution_y
SHIFT_X = -0.23        # push the X-ray product to the right half
D       = 10.0         # person distance from camera
NDC_X   = -0.55        # person centre, screen-left
NDC_Y   = -0.10

def ndc_to_world(nx, ny, d, sx=SHIFT_X, sy=0.0):
    X = (nx/2.0 + sx) * sw * d / lens
    Y = (ny/2.0 * (ry/rx) + sy) * sw * d / lens
    return cpos + fwd*d + camX*X + camY*Y

target_world = ndc_to_world(NDC_X, NDC_Y, D)

# ---- orient the body to face the camera ----
root = bpy.data.objects["P05_WORN_ROOT"]
p_local = Vector((0.0495, -0.7115, 0.099))           # worn device centre in root-local space
to_cam = (cpos - target_world)
theta = math.atan2(to_cam.y, to_cam.x) - math.pi/2.0  # local +Y (body front) -> point at camera
Rz = Matrix.Rotation(theta, 4, 'Z')
T = target_world - (Rz.to_3x3() @ p_local)
root.matrix_basis = Matrix.Translation(T) @ Rz

# ---- aim empty ----
aim = bpy.data.objects.get("P05_WORN_AIM")
if aim is None:
    aim = bpy.data.objects.new("P05_WORN_AIM", None)
    aim.empty_display_type='SPHERE'; aim.empty_display_size=0.15
    bpy.data.collections["P05_WORN"].objects.link(aim)
aim.parent = root; aim.matrix_parent_inverse = Matrix.Identity(4)
aim.matrix_basis = Matrix.Translation(p_local)

# ---- worn lights (placed in camera-relative directions around the person) ----
CL = bpy.data.collections["P05_WORN_LIGHT"]
SPECS = [
    # name,            right,  up,   toward-cam, size, energy, colour
    ("LGT_P05W_Key",   -2.6,   2.1,   2.0,       2.2,  900.0, (1.00, 0.80, 0.60)),
    ("LGT_P05W_Rim_R",  2.4,   1.4,  -2.2,       1.6,  700.0, (0.82, 0.88, 1.00)),
    ("LGT_P05W_Device",-0.9,   0.5,   1.6,       0.7,  180.0, (0.92, 0.95, 1.00)),
    ("LGT_P05W_Fill",  -1.6,  -1.6,   1.4,       2.6,  120.0, (1.00, 0.72, 0.52)),
    ("LGT_P05W_Skin_L",-3.0,  -0.4,  -0.6,       1.8,  420.0, (1.00, 0.62, 0.42)),
]
made=[]
for nm, r, u, t, size, en, col in SPECS:
    o = bpy.data.objects.get(nm)
    if o is None:
        ld = bpy.data.lights.new(nm+"_DATA", 'AREA')
        o = bpy.data.objects.new(nm, ld)
        CL.objects.link(o)
    o.data.type='AREA'; o.data.shape='SQUARE'; o.data.size=size
    o.data.energy=en; o.data.color=col
    o.matrix_basis = Matrix.Translation(target_world + camX*r + camY*u + (-fwd)*t)
    o.constraints.clear()
    c = o.constraints.new('TRACK_TO'); c.target=aim; c.track_axis='TRACK_NEGATIVE_Z'; c.up_axis='UP_Y'
    made.append(nm)

# ---- light linking ----
def linkcoll(name, objs):
    c = bpy.data.collections.get(name)
    if c is None: c = bpy.data.collections.new(name)
    for o in objs:
        if o.name not in c.objects: c.objects.link(o)
    return c
xray_objs = list(bpy.data.collections["P05_XRAY_SHELL"].objects) + \
            list(bpy.data.collections["P05_XRAY_INTERNAL"].objects) + \
            [bpy.data.objects[n] for n in ("X5_STROKE_VOLUME","X5_STROKE_LIMIT_A","X5_STROKE_LIMIT_B")]
worn_objs = list(bpy.data.collections["P05_WORN_PRODUCT"].objects) + list(bpy.data.collections["P05_WORN_BODY"].objects)
LC_X = linkcoll("P05_LINK_XRAY_RECV", xray_objs)
LC_W = linkcoll("P05_LINK_WORN_RECV", worn_objs)

api_ok = hasattr(bpy.data.objects["LGT_P05_Key_Top"], "light_linking")
if api_ok:
    for o in bpy.data.collections["P05_XRAY_LIGHT"].objects:
        o.light_linking.receiver_collection = LC_X
    for nm in made:
        bpy.data.objects[nm].light_linking.receiver_collection = LC_W

bpy.ops.wm.save_mainfile()
out = {"cam_pos":[round(v,3) for v in cpos], "target":[round(v,3) for v in tpos],
       "camX":[round(v,4) for v in camX], "camY":[round(v,4) for v in camY], "fwd":[round(v,4) for v in fwd],
       "person_world":[round(v,3) for v in target_world], "theta_deg": round(math.degrees(theta),2),
       "root_T":[round(v,3) for v in T], "lights": made, "light_linking_api": api_ok,
       "frame_w_at_D": round(sw*D/lens,3), "frame_h_at_D": round(sw*(ry/rx)*D/lens,3)}
print(json.dumps(out, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
