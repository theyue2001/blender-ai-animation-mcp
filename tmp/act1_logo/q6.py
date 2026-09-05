import bpy, json
out={}
sc=[s for s in bpy.data.scenes if "CAM_Opening_Silhouette" in s.objects][0]
F=426
for o in sc.objects:
    if o.type!='LIGHT': continue
    ad=o.data.animation_data
    e=None
    if ad and ad.action:
        for f in ad.action.fcurves:
            if f.data_path=="energy": e=round(f.evaluate(F),2)
    out[o.name]={"E@426": e if e is not None else round(o.data.energy,2),
                 "color":[round(v,3) for v in o.data.color],
                 "size":round(getattr(o.data,'size',0),3),"sy":round(getattr(o.data,'size_y',0),3),
                 "shape":getattr(o.data,'shape',None)}
out["view"]={"vt":sc.view_settings.view_transform,"look":sc.view_settings.look,
             "exposure":sc.view_settings.exposure,"gamma":sc.view_settings.gamma,
             "use_curve":sc.view_settings.use_curve_mapping}
out["exposure_anim"]= [ [round(k.co[0],1),round(k.co[1],3)] for f in (sc.animation_data.action.fcurves if sc.animation_data and sc.animation_data.action else []) if 'exposure' in f.data_path for k in f.keyframe_points ]
print(json.dumps(out, ensure_ascii=False, indent=1))
