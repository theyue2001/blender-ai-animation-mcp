import bpy, json, math
from mathutils import Vector, Matrix, Euler
rep={"lights":[]}
SHOT_START=3000; B1_END=3020; B2_END=3058; SHOT_END=3095
def M_of(loc,rot,scl):
    return Matrix.Translation(loc) @ Euler(rot,'XYZ').to_matrix().to_4x4() @ Matrix.Diagonal(Vector((*scl,1.0)))
def fcval(o,path,idx,frame,default):
    ad=o.animation_data
    if not (ad and ad.action): return default
    for fc in ad.action.fcurves:
        if fc.data_path==path and fc.array_index==idx: return fc.evaluate(frame)
    return default
def clearkeys(idd,path,idx=None):
    ad=idd.animation_data
    if not (ad and ad.action): return
    for fc in list(ad.action.fcurves):
        if fc.data_path==path and (idx is None or fc.array_index==idx):
            ad.action.fcurves.remove(fc)
def setk(idd,path,idx,kvs,interp='SINE',easing='EASE_IN_OUT'):
    for f,v in kvs:
        if idx is None:
            setattr(idd,path,v); idd.keyframe_insert(path,frame=f)
        else:
            cur=idd.path_resolve(path); cur[idx]=v; idd.keyframe_insert(path,index=idx,frame=f)
    for fc in idd.animation_data.action.fcurves:
        if fc.data_path==path and (idx is None or fc.array_index==idx):
            for kp in fc.keyframe_points:
                kp.interpolation=interp
                if interp not in ('CONSTANT','LINEAR'): kp.easing=easing
            fc.update()

# ---- carry the 9 interior bore lights with their sleeve (exact, via local space) ----
for k in "ABC":
    o=bpy.data.objects["P08_CMP_%s"%k]
    old=M_of([fcval(o,'location',i,SHOT_START,o.location[i]) for i in range(3)],
             [fcval(o,'rotation_euler',i,SHOT_START,o.rotation_euler[i]) for i in range(3)], o.scale)
    new=M_of([fcval(o,'location',i,B2_END,o.location[i]) for i in range(3)],
             [fcval(o,'rotation_euler',i,B2_END,o.rotation_euler[i]) for i in range(3)], o.scale)
    oldinv=old.inverted()
    for tag in ("Deep","Mid","Mouth"):
        L=bpy.data.objects["LGT_P08_CMP_%s_%s"%(k,tag)]
        p_old=L.location.copy()
        p_new=new @ (oldinv @ p_old)
        for ax in range(3):
            clearkeys(L,'location',ax)
            setk(L,'location',ax,[(SHOT_START,p_old[ax]),(B1_END,p_old[ax]),(B2_END,p_new[ax])])
        # once the section is open these interior lights blow out - pull them down
        base=L.data.energy if L.data.energy>0 else None
        ad=L.data.animation_data
        cur=None
        if ad and ad.action:
            for fc in ad.action.fcurves:
                if fc.data_path=='energy': cur=fc.evaluate(SHOT_START)
        if cur:
            clearkeys(L.data,'energy')
            setk(L.data,'energy',None,[(2999.2,0.0),(SHOT_START,cur),(B1_END,cur),
                                       (B2_END,cur*0.30),(SHOT_END,cur*0.30),(3096.0,0.0)])
        if L.animation_data and L.animation_data.action:
            L.animation_data.action.name="ACT_P08_LGT_P08_CMP_%s_%s"%(k,tag)
        rep["lights"].append({"n":L.name,"old":[round(v,2) for v in p_old],"new":[round(v,2) for v in p_new],
                              "E":round(cur,1) if cur else None})

# ---- re-aim the three area lights for the top-down section beat ----
# beat1 (end-on) keeps their current placement; beat2 moves them above/behind the sections
AREA={"LGT_P08_CMP_Key":(34.0,2006.0,52.0),
      "LGT_P08_CMP_Fill":(-40.0,2000.0,18.0),
      "LGT_P08_CMP_Rim":(0.0,1944.0,46.0)}
for nm,tgt in AREA.items():
    L=bpy.data.objects[nm]
    p_old=L.location.copy()
    for ax in range(3):
        clearkeys(L,'location',ax)
        setk(L,'location',ax,[(SHOT_START,p_old[ax]),(B1_END,p_old[ax]),(B2_END,tgt[ax])])
    if L.animation_data and L.animation_data.action:
        L.animation_data.action.name="ACT_P08_"+nm
    rep["lights"].append({"n":nm,"old":[round(v,1) for v in p_old],"new":list(tgt)})
bpy.ops.wm.save_mainfile()
rep["saved"]=True
print(json.dumps(rep,indent=1))
