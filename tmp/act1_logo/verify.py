import bpy, json
v={}
o  = bpy.data.objects["P01_DECAL_NITE_R1_Logo_Reveal"]
lo = bpy.data.objects["LGT_Opening_Logo_Highlight"]
m  = bpy.data.materials["MAT_P01_FRONT_LOGO_REVEAL"]
llc= bpy.data.collections["LL_P01_Logo_Highlight"]
v["new_obj_scenes"]   = [s.name for s in bpy.data.scenes if o.name in s.objects]
v["new_light_scenes"] = [s.name for s in bpy.data.scenes if lo.name in s.objects]
v["mat_users"]        = m.users
v["mat_slot"]         = (o.material_slots[0].link, o.material_slots[0].material.name)
v["mesh_shared"]      = (o.data.name, o.data.users)
v["ll_receiver"]      = lo.light_linking.receiver_collection.name if lo.light_linking.receiver_collection else None
v["ll_blocker"]       = lo.light_linking.blocker_collection.name if lo.light_linking.blocker_collection else None
v["ll_members"]       = [x.name for x in llc.objects]
v["ll_in_scenes"]     = [s.name for s in bpy.data.scenes if llc in set(s.collection.children_recursive)]
v["light_cam_vis"]    = lo.visible_camera
# shared/original assets must be untouched
src = bpy.data.materials["SHOT1_NITE_LOGO_DECAL_NITE_R1_Logo_0"]
v["SRC_logo_mat_base"]= [round(x,4) for x in src.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value]
v["SRC_logo_mat_users"]= src.users
p04 = bpy.data.objects["P04_DECAL_NITE_R1_Logo_Reveal"]
v["P04_reveal_mat"]   = (p04.material_slots[0].link, p04.material_slots[0].material.name)
v["P04_reveal_keys"]  = [(f.data_path,[int(k.co[0]) for k in f.keyframe_points]) for f in p04.animation_data.action.fcurves]
v["P04_reveal_scenes"]= [s.name for s in bpy.data.scenes if p04.name in s.objects]
# our animation
v["fade_keys"]  = [[round(k.co[0],1),round(k.co[1],3)] for k in m.node_tree.animation_data.action.fcurves[0].keyframe_points]
v["energy_keys"]= [[round(k.co[0],1),round(k.co[1],3)] for k in lo.data.animation_data.action.fcurves[0].keyframe_points]
v["peak_energy_at_198"] = round(lo.data.animation_data.action.fcurves[0].evaluate(198),3)
bpy.ops.wm.save_mainfile()
v["file"]=bpy.data.filepath.split("\\")[-1]; v["dirty_after_save"]=bpy.data.is_dirty
print(json.dumps(v, ensure_ascii=False, indent=1))
