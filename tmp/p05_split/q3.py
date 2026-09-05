import bpy, json
from mathutils import Vector
out = {}
sc = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
cam = sc.camera
act = cam.animation_data.action
out["cam_fcurves"] = {}
for fc in act.fcurves:
    key = "%s[%d]" % (fc.data_path, fc.array_index)
    out["cam_fcurves"][key] = [[round(k.co[0]), round(k.co[1],4)] for k in fc.keyframe_points]
d = cam.data
out["cam_data_anim"] = None
if d.animation_data and d.animation_data.action:
    out["cam_data_anim"] = {("%s[%d]"%(fc.data_path,fc.array_index)): [[round(k.co[0]), round(k.co[1],3)] for k in fc.keyframe_points] for fc in d.animation_data.action.fcurves}
out["cam_sensor"] = [d.sensor_width, d.sensor_fit]
# scene 01 human
sc1 = bpy.data.scenes["01_SCN_OPENING_P01_P03"]
out["sc1_objs"] = [[o.name, o.type, o.instance_type if o.type=='EMPTY' else "", (o.instance_collection.name if getattr(o,'instance_collection',None) else "")] for o in sc1.objects]
src = bpy.data.collections.get("SRC_OPENING_HUMAN_LINKED")
if src:
    out["human_coll"] = [[o.name, o.type, len(o.data.vertices) if o.type=='MESH' else 0, o.parent.name if o.parent else None] for o in src.objects]
inst = bpy.data.objects.get("INST_Opening_Human")
if inst:
    out["inst_human"] = {"loc":[round(v,3) for v in inst.location], "rot":[round(v,3) for v in inst.rotation_euler],
                         "scale":[round(v,4) for v in inst.scale], "coll": inst.instance_collection.name if inst.instance_collection else None,
                         "offset":[round(v,3) for v in inst.instance_collection.instance_offset] if inst.instance_collection else None}
# world bbox of Male computed analytically
def world_mat(o):
    import mathutils
    m = o.matrix_basis.copy()
    p = o.parent
    while p:
        m = p.matrix_basis @ o.matrix_parent_inverse @ m if False else m
        break
    return o.matrix_local
male = bpy.data.objects.get("Male")
if male:
    bb = [Vector(c) for c in male.bound_box]
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    out["male_local_bbox"] = [[round(v,3) for v in mn],[round(v,3) for v in mx]]
    out["male_matrix_local"] = [[round(x,4) for x in r] for r in male.matrix_local]
    out["male_parent"] = male.parent.name if male.parent else None
    out["male_users_coll"] = [c.name for c in male.users_collection]
print(json.dumps(out, ensure_ascii=False, indent=1))
