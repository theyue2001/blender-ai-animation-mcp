import bpy, json
out={}
out["file"]=bpy.data.filepath
out["scenes"]=[s.name for s in bpy.data.scenes]
sc=bpy.data.scenes.get("SCN_P08_SLEEVE_TUNNEL")
if sc:
    out["range"]=[sc.frame_start,sc.frame_end,sc.render.fps]
    out["markers"]=sorted([(m.frame,m.name,m.camera.name if m.camera else None) for m in sc.timeline_markers])[:12]
for n in ["P08_TRAIL_BLUE","P08_TRAIL_PINK","P08_FXDOT_BLUE","P08_FXDOT_PINK","P08_TRAIL_TAPER"]:
    o=bpy.data.objects.get(n)
    if not o: out[n]="MISSING"; continue
    d={"type":o.type,"loc":[round(v,4) for v in o.location],"scale":[round(v,4) for v in o.scale],
       "parent":o.parent.name if o.parent else None,
       "constraints":[(c.type,getattr(c,'target',None).name if getattr(c,'target',None) else None, round(getattr(c,'offset_factor',-1),4)) for c in o.constraints]}
    if o.type=='CURVE':
        d["bevel_depth"]=round(o.data.bevel_depth,5)
        d["bevel_object"]=o.data.bevel_object.name if o.data.bevel_object else None
        d["taper"]=o.data.taper_object.name if o.data.taper_object else None
        d["res"]=[o.data.bevel_resolution,o.data.resolution_u]
        d["bf"]=[round(o.data.bevel_factor_start,4),round(o.data.bevel_factor_end,4)]
        d["pts"]=[len(sp.points)+len(sp.bezier_points) for sp in o.data.splines]
    if o.type=='MESH':
        d["dims"]=[round(v,4) for v in o.dimensions]
    ad=o.animation_data
    d["fcurves"]=sorted(set((f.data_path,f.array_index) for f in ad.action.fcurves)) if (ad and ad.action) else None
    if ad and ad.action:
        d["action"]=ad.action.name
        d["frange"]=[round(v,1) for v in ad.action.frame_range]
    dad=o.data.animation_data if hasattr(o.data,'animation_data') else None
    d["data_fcurves"]=sorted(set((f.data_path,f.array_index) for f in dad.action.fcurves)) if (dad and dad.action) else None
    out[n]=d
cam=bpy.data.objects.get("CAM_P08_01_Activation")
if cam:
    out["cam"]={"loc":[round(v,3) for v in cam.location],"rot":[round(v,4) for v in cam.rotation_euler],
                "lens":cam.data.lens,"sensor":cam.data.sensor_width}
print(json.dumps(out,indent=1,ensure_ascii=False))
