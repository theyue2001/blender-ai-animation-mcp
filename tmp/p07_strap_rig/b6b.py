import bpy, math
from mathutils import Vector, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
rig = bpy.data.collections["P07_RIG"]
log = []
W_BOX = bpy.data.objects["WGT_P07_BOX"]
W_FLAT = bpy.data.objects["WGT_P07_FLAT"]
W_RING = bpy.data.objects["WGT_P07_RING"]
RED = ("BUCKLE", "ENTRY", "END")

for tag in ("StrapUpper", "StrapLower"):
    ao = bpy.data.objects["NITE_" + tag + "_Armature"]
    for pb in ao.pose.bones:
        pb.rotation_mode = 'XYZ'
        nm = pb.name
        if nm.endswith("_MASTER"):
            pb.custom_shape = W_RING; pb.custom_shape_scale_xyz = (2.8, 2.8, 2.8)
            pb.bone.color.palette = 'THEME09'
        elif nm.endswith("_CTRL"):
            key = nm[len(tag) + 1:-5]
            pb.custom_shape = W_FLAT; pb.custom_shape_scale_xyz = (1.7, 1.7, 1.7)
            pb.bone.color.palette = 'THEME01' if key in RED else ('THEME06' if key == "ROOT" else 'THEME04')
        elif "_CP_" in nm:
            pb.custom_shape = W_BOX; pb.custom_shape_scale_xyz = (0.85, 0.85, 0.85)
            pb.bone.color.palette = 'THEME11'
        pb.use_custom_shape_bone_size = True
    ao.show_in_front = True

RN = "NITE_Strap_Rig_ROOT"
ro = bpy.data.objects.get(RN)
if ro is None:
    ro = bpy.data.objects.new(RN, None)
    ro.empty_display_type = 'ARROWS'; ro.empty_display_size = 0.55
    rig.objects.link(ro)
T = Matrix.Translation(Vector((0.0499, -1.5200, 0.6500)))
ro.matrix_world = T
Ti = T.inverted()
for k in ["P07_STRAP_UPPER", "P07_STRAP_LOWER", "NITE_StrapUpper_Armature",
          "NITE_StrapLower_Armature", "CRV_StrapUpper_Path", "CRV_StrapLower_Path"]:
    o = bpy.data.objects[k]
    mw = o.matrix_world.copy()
    o.parent = ro
    o.matrix_parent_inverse = Ti
    o.matrix_basis = mw
log.append("widgets + colours applied; %d objects parented to %s at %s" %
           (6, RN, tuple(round(v, 3) for v in ro.location)))
for tag in ("StrapUpper", "StrapLower"):
    ao = bpy.data.objects["NITE_" + tag + "_Armature"]
    log.append("%s: %d bones (%d deform, %d CP, %d semantic)" %
               (ao.name, len(ao.data.bones),
                sum(1 for b in ao.data.bones if b.use_deform),
                sum(1 for b in ao.data.bones if "_CP_" in b.name),
                sum(1 for b in ao.data.bones if b.name.endswith("_CTRL"))))
print("\n".join(log))
