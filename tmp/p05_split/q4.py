import bpy, json
from mathutils import Vector
out = {}
sc = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
cam = sc.camera
out["cam_constraints"] = [[c.type, getattr(c,'target',None).name if getattr(c,'target',None) else None,
                           getattr(c,'track_axis',''), getattr(c,'up_axis','')] for c in cam.constraints]
# target empties
for n in ["X5_STROKE_VOLUME","X5_STROKE_LIMIT_A","X5_STROKE_LIMIT_B","X5_GEAR_SPIN","X5_CTRL"]:
    o = bpy.data.objects.get(n)
    if o: out["obj_"+n] = {"loc":[round(v,3) for v in o.location], "type":o.type, "parent": o.parent.name if o.parent else None}
# rig collection contents
rig = bpy.data.collections.get("P05_XRAY_RIG")
if rig: out["rig_objs"] = [[o.name,o.type,[round(v,3) for v in o.location]] for o in rig.objects]
# Male true size
male = bpy.data.objects.get("Male")
out["male_dims"] = [round(v,3) for v in male.dimensions]
out["male_scale"] = [round(v,4) for v in male.scale]
out["male_delta_scale"] = [round(v,4) for v in male.delta_scale]
out["male_delta_loc"] = [round(v,3) for v in male.delta_location]
out["male_mods"] = [m.type for m in male.modifiers]
out["male_matrix_world"] = [[round(x,3) for x in r] for r in male.matrix_world]
uw = bpy.data.objects.get("Underwear")
out["uw_dims"] = [round(v,3) for v in uw.dimensions]
out["uw_matrix_world"] = [[round(x,3) for x in r] for r in uw.matrix_world]
# scene 01 product instance
inst = bpy.data.objects.get("INST_Opening_NITE_Product")
out["inst_product"] = {"loc":[round(v,3) for v in inst.location], "rot":[round(v,4) for v in inst.rotation_euler],
                       "scale":[round(v,4) for v in inst.scale]}
# scene 01 cameras
sc1 = bpy.data.scenes["01_SCN_OPENING_P01_P03"]
for o in sc1.objects:
    if o.type=='CAMERA':
        out["cam1_"+o.name] = {"lens": round(o.data.lens,1), "loc":[round(v,3) for v in o.location],
                               "rot":[round(v,3) for v in o.rotation_euler],
                               "cons":[[c.type, getattr(c,'target',None).name if getattr(c,'target',None) else None] for c in o.constraints],
                               "dof": o.data.dof.use_dof, "focus_obj": o.data.dof.focus_object.name if o.data.dof.focus_object else None,
                               "focus": round(o.data.dof.focus_distance,3), "fstop": round(o.data.dof.aperture_fstop,2)}
    if o.type=='EMPTY' and o.name.startswith("CTRL"):
        out["ctrl_"+o.name]=[round(v,3) for v in o.location]
print(json.dumps(out, ensure_ascii=False, indent=1))
