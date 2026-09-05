import bpy, math
from mathutils import Vector, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
root = bpy.data.collections["P07_STRAP_RIG"]
rig = bpy.data.collections["P07_RIG"]
log = []

# ---- widget collection -------------------------------------------------
if "P07_WIDGETS" not in bpy.data.collections:
    wc = bpy.data.collections.new("P07_WIDGETS")
    root.children.link(wc)
    wc.hide_render = True
    lc = sc.view_layers[0].layer_collection.children["P07_STRAP_RIG"].children["P07_WIDGETS"]
    lc.exclude = True
wc = bpy.data.collections["P07_WIDGETS"]


def wgt_box(name, sx=1.0, sy=1.0, sz=1.0):
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    me = bpy.data.meshes.new(name)
    v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
         (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    e = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    me.from_pydata(v, e, [])
    me.update()
    o = bpy.data.objects.new(name, me)
    wc.objects.link(o); o.hide_render = True
    return o


def wgt_ring(name, r=1.0, n=32):
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    me = bpy.data.meshes.new(name)
    v = [(r*math.cos(2*math.pi*i/n), r*math.sin(2*math.pi*i/n), 0.0) for i in range(n)]
    e = [(i, (i+1) % n) for i in range(n)]
    me.from_pydata(v, e, [])
    me.update()
    o = bpy.data.objects.new(name, me)
    wc.objects.link(o); o.hide_render = True
    return o


W_BOX = wgt_box("WGT_P07_BOX", 0.30, 0.30, 0.30)
W_FLAT = wgt_box("WGT_P07_FLAT", 0.45, 0.16, 0.30)
W_RING = wgt_ring("WGT_P07_RING", 1.0)

RED = ("BUCKLE", "ENTRY", "END")
for tag in ("StrapUpper", "StrapLower"):
    ao = bpy.data.objects["NITE_" + tag + "_Armature"]
    for pb in ao.pose.bones:
        pb.rotation_mode = 'XYZ'
        nm = pb.name
        if nm.endswith("_MASTER"):
            pb.custom_shape = W_RING; pb.custom_shape_scale_xyz = (2.6, 2.6, 2.6)
        elif nm.endswith("_CTRL"):
            key = nm.split("_", 1)[1].rsplit("_CTRL", 1)[0]
            pb.custom_shape = W_FLAT if key in RED or key == "ROOT" else W_BOX
            pb.custom_shape_scale_xyz = (1.4, 1.4, 1.4)
            pb.bone.color.palette = 'THEME01' if key in RED else ('THEME06' if key == "ROOT" else 'THEME04')
        pb.use_custom_shape_bone_size = True
    ao.show_in_front = True

# ---- master rig root ---------------------------------------------------
RN = "NITE_Strap_Rig_ROOT"
if RN in bpy.data.objects:
    ro = bpy.data.objects[RN]
else:
    ro = bpy.data.objects.new(RN, None)
    ro.empty_display_type = 'ARROWS'
    ro.empty_display_size = 0.55
    rig.objects.link(ro)
T = Matrix.Translation(Vector((0.0499, -1.5200, 0.6500)))
ro.matrix_world = T
Ti = T.inverted()
kids = ["P07_STRAP_UPPER", "P07_STRAP_LOWER",
        "NITE_StrapUpper_Armature", "NITE_StrapLower_Armature",
        "CRV_StrapUpper_Path", "CRV_StrapLower_Path"]
for k in kids:
    o = bpy.data.objects[k]
    mw = o.matrix_world.copy()
    o.parent = ro
    o.matrix_parent_inverse = Ti
    o.matrix_basis = mw
    log.append("parented %s (world preserved: %s)" % (k, tuple(round(v, 4) for v in (T @ Ti @ mw).to_translation())))
log.append("rig root %s at %s" % (RN, tuple(round(v, 3) for v in ro.location)))
print("\n".join(log))
