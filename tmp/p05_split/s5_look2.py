import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
for nm, en in (("LGT_P05W_Key",150.0), ("LGT_P05W_Rim_R",330.0), ("LGT_P05W_Device",110.0),
               ("LGT_P05W_Fill",10.0), ("LGT_P05W_Skin_L",45.0)):
    bpy.data.objects[nm].data.energy = en
sk = bpy.data.materials["MAT_P05W_HUMAN_Male_0"].node_tree.nodes["Principled BSDF"]
sk.inputs["Base Color"].default_value = (0.085, 0.038, 0.028, 1.0)
d = SC.camera.data.dof
info = {"use_dof": d.use_dof, "focus_obj": d.focus_object.name if d.focus_object else None,
        "focus_dist": round(d.focus_distance,3), "fstop": round(d.aperture_fstop,3),
        "dof_anim": bool(SC.camera.data.animation_data and SC.camera.data.animation_data.action)}
bpy.ops.wm.save_mainfile()
print(json.dumps(info))
bpy.context.window.scene = prev
