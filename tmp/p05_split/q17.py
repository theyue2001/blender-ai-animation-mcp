import bpy, json
out={}
worn = list(bpy.data.collections["P05_WORN_BODY"].objects)[0]
out["hide_render_keys"]=[[round(k.co[0]),round(k.co[1],2)] for k in worn.animation_data.action.fcurves.find("hide_render").keyframe_points]
d=bpy.data.objects["LGT_P05W_Key"].data
out["key_light_keys"]=[[round(k.co[0]),round(k.co[1],1)] for k in d.animation_data.action.fcurves.find("energy").keyframe_points]
nt=bpy.data.materials["MAT_P05W_Control_Plate"].node_tree
fc=nt.animation_data.action.fcurves.find('nodes["KEY_UP"].outputs[0].default_value')
out["press_keys"]=[[round(k.co[0]),round(k.co[1],2)] for k in fc.keyframe_points]
nt2=bpy.data.materials["MAT_P05W_LED_Amber"].node_tree
out["amber_keys"]=[[round(k.co[0]),round(k.co[1],2)] for k in nt2.animation_data.action.fcurves.find('nodes["EMIS"].inputs[1].default_value').keyframe_points]
SC=bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
out["range"]=[SC.frame_start,SC.frame_end]; out["n"]=SC.frame_end-SC.frame_start+1
out["sec"]=round(out["n"]/(SC.render.fps/SC.render.fps_base),2)
print(json.dumps(out, ensure_ascii=False, indent=1))
