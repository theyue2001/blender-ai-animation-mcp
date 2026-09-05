import bpy, json
out = {}
for n in ["X5_CARRIAGE","X5_MOTOR_SPIN","X5_GEAR_SPIN","X5_CAM_TARGET","X5_MOTOR_TARGET"]:
    o = bpy.data.objects.get(n)
    if not o: continue
    d = {"children":[c.name for c in bpy.data.objects if c.parent==o]}
    ad = o.animation_data
    if ad and ad.action:
        d["action"]=ad.action.name
        for fc in ad.action.fcurves:
            kp = fc.keyframe_points
            d["%s[%d]"%(fc.data_path,fc.array_index)] = {"n":len(kp), "first":[round(kp[0].co[0]),round(kp[0].co[1],4)],
                "last":[round(kp[-1].co[0]),round(kp[-1].co[1],4)],
                "sample":[[round(kp[i].co[0]),round(kp[i].co[1],4)] for i in range(0,len(kp),max(1,len(kp)//14))][:16]}
        d["drivers"]=[]
    if ad and ad.drivers:
        d["drivers"]=[[dr.data_path, dr.driver.expression] for dr in ad.drivers]
    out[n]=d
print(json.dumps(out, ensure_ascii=False, indent=1))
