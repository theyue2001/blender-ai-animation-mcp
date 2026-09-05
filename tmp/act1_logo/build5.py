import bpy, json
log={}
o = bpy.data.objects["49.002"]
MATN = "MAT_P01_CONTROL_BUTTONS"
old = bpy.data.materials.get(MATN)
if old: bpy.data.materials.remove(old); log["removed_old"]=True

srcm = bpy.data.materials["SHOT1_CONTROL_49.002_0"]
m = srcm.copy(); m.name = MATN
if m.node_tree: m.node_tree.animation_data_clear()      # drop the dormant P04 ignition curve
ign = m.node_tree.nodes.get("IGNITION_Glow_Emission")
if ign: ign.inputs[1].default_value = 0.0

# isolate: only object 49.002 in scene 01 gets this material
o.material_slots[0].link = 'OBJECT'
o.material_slots[0].material = m

p = m.node_tree.nodes["Principled BSDF"]
BASE = (0.7922, 0.8196, 0.9333)
# hold the approved look to f250, then roll reflectance back as the rim/key lights spike
FAC = [(1,1.0),(250,1.0),(300,0.612),(350,0.468),(400,0.431),(450,0.431)]
RGH = [(1,0.5528),(250,0.5528),(300,0.600),(350,0.640),(400,0.660),(450,0.660)]
for f,k in FAC:
    p.inputs["Base Color"].default_value = (BASE[0]*k, BASE[1]*k, BASE[2]*k, 1.0)
    p.inputs["Base Color"].keyframe_insert("default_value", frame=f)
for f,v in RGH:
    p.inputs["Roughness"].default_value = v
    p.inputs["Roughness"].keyframe_insert("default_value", frame=f)
act = m.node_tree.animation_data.action
act.name = "ACT_Opening_P01_ControlButtons_Exposure"
for fc in act.fcurves:
    for k in fc.keyframe_points:
        k.interpolation='BEZIER'; k.easing='EASE_IN_OUT'
    fc.update()

log["slot"]=(o.material_slots[0].link, o.material_slots[0].material.name)
log["mat_users"]=m.users
log["src_mat_untouched"]=[round(v,4) for v in srcm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value]
log["src_mat_objs"]=[ob.name for ob in bpy.data.objects if ob.type=='MESH' and any(s.material==srcm for s in ob.material_slots)]
log["curve"]={fc.data_path+"[%d]"%fc.array_index: [[round(k.co[0],1),round(k.co[1],4)] for k in fc.keyframe_points] for fc in act.fcurves}
bpy.ops.wm.save_mainfile(); log["saved"]=True
print(json.dumps(log, ensure_ascii=False, indent=1))
