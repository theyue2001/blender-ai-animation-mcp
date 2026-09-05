import bpy, json
log={}
m  = bpy.data.materials["MAT_P01_FRONT_LOGO_REVEAL"]
nt = m.node_tree
fade = nt.nodes["SHOT1_NITE_LOGO_Fade"]
ld = bpy.data.objects["LGT_Opening_Logo_Highlight"].data
PEAK = 2.0

# opacity comes up early and quickly; while it does, the light is still ~0 so nothing shows
FADE = [(1,0.0),(120,0.0),(132,0.40),(145,1.0),(450,1.0)]
# energy follows t**2.4 over 130..198 so the RISE LOOKS EVEN after AgX, not back-loaded
ENER = [(1,0.0),(130,0.0),(140,0.020),(150,0.106),(160,0.278),(170,0.560),
        (180,0.955),(190,1.472),(198,PEAK),(450,PEAK)]

nt.animation_data_clear()
for f,v in FADE:
    fade.inputs[0].default_value = v
    fade.inputs[0].keyframe_insert("default_value", frame=f)
nt.animation_data.action.name = "ACT_Opening_P01_LogoReveal_Fade"

ld.animation_data_clear()
for f,v in ENER:
    ld.energy = v
    ld.keyframe_insert("energy", frame=f)
ld.animation_data.action.name = "ACT_Opening_LGT_Logo_Highlight"

for act in (nt.animation_data.action, ld.animation_data.action):
    for fc in act.fcurves:
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'    # curve shape is baked into the key values
        fc.update()
# flat hold on the tail
for fc in ld.animation_data.action.fcurves:
    fc.keyframe_points[-1].interpolation='LINEAR'

def dump(ad):
    return {f.data_path:[[round(k.co[0],1),round(k.co[1],3)] for k in f.keyframe_points] for f in ad.action.fcurves}
log["fade"]=dump(nt.animation_data); log["energy"]=dump(ld.animation_data)
bpy.ops.wm.save_mainfile(); log["saved"]=True
print(json.dumps(log, indent=1))
