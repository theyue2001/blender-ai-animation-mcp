import bpy, json, math
from mathutils import Vector
rep={}
SHOT_START=3000; B1_END=3020; B2_END=3058; SHOT_END=3095
E=math.radians(50.0); D=87.1; GY=1971.0
def clearkeys(idd,path,idx=None):
    ad=idd.animation_data
    if not (ad and ad.action): return
    for fc in list(ad.action.fcurves):
        if fc.data_path==path and (idx is None or fc.array_index==idx):
            ad.action.fcurves.remove(fc)
def setk(idd,path,idx,kvs,interp='SINE',easing='EASE_IN_OUT'):
    for f,v in kvs:
        if idx is None: setattr(idd,path,v); idd.keyframe_insert(path,frame=f)
        else:
            cur=idd.path_resolve(path); cur[idx]=v; idd.keyframe_insert(path,index=idx,frame=f)
    for fc in idd.animation_data.action.fcurves:
        if fc.data_path==path and (idx is None or fc.array_index==idx):
            for kp in fc.keyframe_points:
                kp.interpolation=interp
                if interp not in ('CONSTANT','LINEAR'): kp.easing=easing
            fc.update()

# ---- 1. camera: correct distance so nothing crops ----
cam=bpy.data.objects["CAM_P08_05_Compare"]
C2=Vector((0.0, GY+D*math.cos(E), D*math.sin(E)))
view=Vector((0.0,-math.cos(E),-math.sin(E)))
C3=C2+view*15.1                      # beat-3 push for the texture close-up
for ax in range(3): clearkeys(cam,'location',ax)
clearkeys(cam,'rotation_euler',0)
setk(cam,'location',0,[(SHOT_START,0.0),(B1_END,0.0),(B2_END,C2.x),(SHOT_END,C3.x)])
setk(cam,'location',1,[(SHOT_START,2036.0),(B1_END,2030.0),(B2_END,C2.y),(SHOT_END,C3.y)])
setk(cam,'location',2,[(SHOT_START,1.0),(B1_END,3.0),(B2_END,C2.z),(SHOT_END,C3.z)])
setk(cam,'rotation_euler',0,[(SHOT_START,math.radians(90.0)),(B1_END,math.radians(90.0)),
                             (B2_END,math.radians(40.0)),(SHOT_END,math.radians(40.0))])
clearkeys(cam.data,'lens')
setk(cam.data,'lens',None,[(SHOT_START,21.0),(B1_END,22.0),(B2_END,32.0),(SHOT_END,38.0)])
rep["cam"]={"B2":[round(v,2) for v in C2],"END":[round(v,2) for v in C3],
            "rotX_deg":40.0,"lens":[21,22,32,38]}

# ---- 2. exposure: the section beat was ~3 stops hot ----
INT={"Deep":0.08,"Mid":0.08,"Mouth":0.08}
for k in "ABC":
    for tag,f in INT.items():
        L=bpy.data.objects["LGT_P08_CMP_%s_%s"%(k,tag)]
        fc=[c for c in L.data.animation_data.action.fcurves if c.data_path=='energy'][0]
        base=fc.evaluate(SHOT_START)
        clearkeys(L.data,'energy')
        setk(L.data,'energy',None,[(2999.2,0.0),(SHOT_START,base),(B1_END,base),
                                   (B2_END,base*f),(SHOT_END,base*f),(3096.0,0.0)])
AREA={"LGT_P08_CMP_Key":8500.0,"LGT_P08_CMP_Fill":2200.0,"LGT_P08_CMP_Rim":10000.0}
for nm,tgt in AREA.items():
    L=bpy.data.objects[nm]
    fc=[c for c in L.data.animation_data.action.fcurves if c.data_path=='energy'][0]
    base=fc.evaluate(SHOT_START)
    clearkeys(L.data,'energy')
    setk(L.data,'energy',None,[(2999.2,0.0),(SHOT_START,base),(B1_END,base),
                               (B2_END,tgt),(SHOT_END,tgt),(3096.0,0.0)])
    rep.setdefault("area",{})[nm]=[base,tgt]

# ---- 3. cut face needs a flipped normal or backfaces shade black ----
for k in "ABC":
    nt=bpy.data.materials["MAT_P08_CMPSEC_%s"%k].node_tree
    face=nt.nodes["CUT_FACE"]; geo=nt.nodes["CUT_GEO"]
    if "CUT_FLIP" in nt.nodes: nt.nodes.remove(nt.nodes["CUT_FLIP"])
    flip=nt.nodes.new("ShaderNodeVectorMath"); flip.name="CUT_FLIP"
    flip.operation='SCALE'; flip.location=(-700,-320)
    nt.links.new(geo.outputs["Normal"], flip.inputs[0])
    flip.inputs["Scale"].default_value=-1.0
    nt.links.new(flip.outputs["Vector"], face.inputs["Normal"])
bpy.ops.wm.save_mainfile()
rep["saved"]=True
print(json.dumps(rep,indent=1))
