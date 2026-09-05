import bpy, json
log={}
m  = bpy.data.materials["MAT_P01_FRONT_LOGO_REVEAL"]
nt = m.node_tree
fade = nt.nodes["SHOT1_NITE_LOGO_Fade"]
lo = bpy.data.objects["LGT_Opening_Logo_Highlight"]
ld = lo.data
o  = bpy.data.objects["P01_DECAL_NITE_R1_Logo_Reveal"]
llc = bpy.data.collections["LL_P01_Logo_Highlight"]

# the human must never be able to shadow the logo highlight
try:
    lo.light_linking.blocker_collection = llc
    log["blocker"]="ok"
except Exception as e:
    log["blocker"]="FAILED %r"%(e,)

# ---- reveal ramp: gradual emergence, fully highlighted at frame 198 ----
FADE = [(1,0.0),(150,0.0),(168,0.10),(184,0.48),(198,1.0),(450,1.0)]
ENER = [(1,0.0),(150,0.0),(168,0.15),(184,0.90),(198,2.0),(450,2.0)]

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
            k.interpolation = 'BEZIER'
            k.easing = 'EASE_IN_OUT'
        fc.update()

def dump(ad):
    a=ad.action
    return {f.data_path: [[round(k.co[0],1), round(k.co[1],3)] for k in f.keyframe_points] for f in a.fcurves}
log["fade"]=dump(nt.animation_data)
log["energy"]=dump(ld.animation_data)
log["mat_users"]=m.users
log["obj_scenes"]=[s.name for s in bpy.data.scenes if o.name in s.objects]
log["lgt_scenes"]=[s.name for s in bpy.data.scenes if lo.name in s.objects]
bpy.ops.wm.save_mainfile()
log["saved"]=True
print(json.dumps(log, indent=1))
