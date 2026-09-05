import bpy, json, math
from mathutils import Vector, Matrix, Euler
rep={"steps":[]}
SC=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]

B1_END=3020; B2_END=3058; SHOT_END=3095; SHOT_START=3000
ELEV=math.radians(55.0)
GROUP=Vector((0.0,1971.0,0.0)); SPACING=26.0

def clearkeys(idd,path,idx=None):
    ad=idd.animation_data
    if not (ad and ad.action): return
    for fc in list(ad.action.fcurves):
        if fc.data_path==path and (idx is None or fc.array_index==idx):
            ad.action.fcurves.remove(fc)
def setk(idd,path,idx,kvs,interp='BEZIER',easing='AUTO'):
    for f,v in kvs:
        if idx is None:
            if "." in path:
                head,tail=path.rsplit(".",1); setattr(idd.path_resolve(head),tail,v)
            else: setattr(idd,path,v)
            idd.keyframe_insert(path,frame=f)
        else:
            cur=idd.path_resolve(path); cur[idx]=v
            idd.keyframe_insert(path,index=idx,frame=f)
    for fc in idd.animation_data.action.fcurves:
        if fc.data_path==path and (idx is None or fc.array_index==idx):
            for kp in fc.keyframe_points:
                kp.interpolation=interp
                if interp not in ('CONSTANT','LINEAR'): kp.easing=easing
            fc.update()

# ---------- 1. sectioned material copies ----------
FINAL_ROT={"A":(0.0,0.0,0.0),"B":(math.radians(-180.0),0.0,0.0),"C":(math.radians(90.0),0.0,0.0)}
TARGET_X={"A":0.0,"B":-SPACING,"C":SPACING}
for k in "ABC":
    o=bpy.data.objects["P08_CMP_%s"%k]
    src=bpy.data.materials["MAT_P08_SLEEVE_%s"%k]
    nm="MAT_P08_CMPSEC_%s"%k
    m=bpy.data.materials.get(nm)
    if m is None:
        m=src.copy(); m.name=nm
    o.material_slots[0].link='OBJECT'
    o.material_slots[0].material=m
    nt=m.node_tree
    for junk in ("CUT_GEO","CUT_SEP","CUT_VAL","CUT_GT","CUT_FACE","CUT_MIXBF","CUT_TRANS","CUT_MIX"):
        if junk in nt.nodes: nt.nodes.remove(nt.nodes[junk])
    prin=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    out =next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
    geo=nt.nodes.new("ShaderNodeNewGeometry"); geo.name="CUT_GEO"; geo.location=(-900,300)
    sep=nt.nodes.new("ShaderNodeSeparateXYZ"); sep.name="CUT_SEP"; sep.location=(-700,380)
    val=nt.nodes.new("ShaderNodeValue"); val.name="CUT_VAL"; val.location=(-700,220)
    val.outputs[0].default_value=12.0
    gt =nt.nodes.new("ShaderNodeMath"); gt.name="CUT_GT"; gt.operation='GREATER_THAN'; gt.location=(-500,300)
    face=nt.nodes.new("ShaderNodeBsdfPrincipled"); face.name="CUT_FACE"; face.location=(-500,-260)
    face.inputs["Base Color"].default_value=(0.62,0.61,0.60,1.0)
    face.inputs["Roughness"].default_value=0.52
    face.inputs["Specular IOR Level"].default_value=0.35
    mbf=nt.nodes.new("ShaderNodeMixShader"); mbf.name="CUT_MIXBF"; mbf.location=(-200,0)
    tr =nt.nodes.new("ShaderNodeBsdfTransparent"); tr.name="CUT_TRANS"; tr.location=(-200,-300)
    mx =nt.nodes.new("ShaderNodeMixShader"); mx.name="CUT_MIX"; mx.location=(60,60)
    L=nt.links
    L.new(geo.outputs["Position"], sep.inputs[0])
    L.new(sep.outputs["Z"], gt.inputs[0]); L.new(val.outputs[0], gt.inputs[1])
    L.new(geo.outputs["Backfacing"], mbf.inputs[0])
    L.new(prin.outputs[0], mbf.inputs[1]); L.new(face.outputs[0], mbf.inputs[2])
    L.new(gt.outputs[0], mx.inputs[0])
    L.new(mbf.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs["Surface"])
    nt.animation_data_create()
    clearkeys(nt,'nodes["CUT_VAL"].outputs[0].default_value')
    for f,v in [(SHOT_START,12.0),(B1_END+6,12.0),(B2_END,-1.5)]:
        val.outputs[0].default_value=v
        nt.keyframe_insert('nodes["CUT_VAL"].outputs[0].default_value',frame=f)
    for fc in nt.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation='SINE'; kp.easing='EASE_IN_OUT'
        fc.update()
    if nt.animation_data.action: nt.animation_data.action.name="ACT_P08_CUT_%s"%k

    # ---------- 2. object move / rotate into the section layout ----------
    lb=[Vector(c) for c in o.bound_box]
    lmn=Vector((min(p[i] for p in lb) for i in range(3))); lmx=Vector((max(p[i] for p in lb) for i in range(3)))
    c_local=(lmn+lmx)*0.5
    R=Euler(FINAL_ROT[k],'XYZ').to_matrix().to_4x4()
    S=Matrix.Diagonal(Vector((*o.scale,1.0)))
    target_centre=Vector((TARGET_X[k],GROUP.y,0.0))
    loc_final=target_centre-((R@S)@c_local)
    loc_start=o.location.copy(); rot_start=[v for v in o.rotation_euler]
    for ax in range(3):
        setk(o,'location',ax,[(SHOT_START,loc_start[ax]),(B1_END,loc_start[ax]),
                              (B2_END,loc_final[ax])],'SINE','EASE_IN_OUT')
        setk(o,'rotation_euler',ax,[(SHOT_START,rot_start[ax]),(B1_END,rot_start[ax]),
                                    (B2_END,FINAL_ROT[k][ax])],'SINE','EASE_IN_OUT')
    if o.animation_data and o.animation_data.action:
        o.animation_data.action.name="ACT_P08_P08_CMP_%s"%k
    rep["steps"].append({"k":k,"loc_start":[round(v,2) for v in loc_start],
        "loc_final":[round(v,2) for v in loc_final],
        "rot_final_deg":[round(math.degrees(v),1) for v in FINAL_ROT[k]],
        "target_centre":[round(v,2) for v in target_centre]})

# ---------- 3. camera ----------
cam=bpy.data.objects["CAM_P08_05_Compare"]
D=73.9
Cs=Vector((0.0, GROUP.y+D*math.cos(ELEV), D*math.sin(ELEV)))
view=Vector((0.0,-math.cos(ELEV),-math.sin(ELEV)))
Cend=Cs+view*20.0
for ax in range(3): clearkeys(cam,'location',ax)
clearkeys(cam,'rotation_euler',0); clearkeys(cam,'rotation_euler',1); clearkeys(cam,'rotation_euler',2)
setk(cam,'location',0,[(SHOT_START,0.0),(B1_END,0.0),(B2_END,Cs.x),(SHOT_END,Cend.x)],'SINE','EASE_IN_OUT')
setk(cam,'location',1,[(SHOT_START,2036.0),(B1_END,2028.0),(B2_END,Cs.y),(SHOT_END,Cend.y)],'SINE','EASE_IN_OUT')
setk(cam,'location',2,[(SHOT_START,1.0),(B1_END,3.0),(B2_END,Cs.z),(SHOT_END,Cend.z)],'SINE','EASE_IN_OUT')
setk(cam,'rotation_euler',0,[(SHOT_START,math.radians(90.0)),(B1_END,math.radians(90.0)),
                             (B2_END,math.radians(35.0)),(SHOT_END,math.radians(35.0))],'SINE','EASE_IN_OUT')
cam.rotation_euler[1]=0.0; cam.rotation_euler[2]=math.radians(180.0)
cam.data.animation_data_create()
clearkeys(cam.data,'lens')
setk(cam.data,'lens',None,[(SHOT_START,21.0),(B1_END,23.0),(B2_END,35.0),(SHOT_END,42.0)],'SINE','EASE_IN_OUT')
if cam.animation_data.action: cam.animation_data.action.name="ACT_P08_CAM_P08_05_Compare"
rep["cam"]={"B2":[round(v,2) for v in Cs],"END":[round(v,2) for v in Cend],"rotX_deg":35.0,"D":D}

# ---------- 4. what lights this beat? ----------
rep["lights"]=[]
for o in SC.objects:
    if o.type=='LIGHT' and o.matrix_world.translation.y>1800:
        ad=o.data.animation_data
        rep["lights"].append({"n":o.name,"type":o.data.type,"E":round(o.data.energy,1),
            "loc":[round(v,1) for v in o.location],
            "size":round(getattr(o.data,'size',0.0),2),
            "keys":{f.data_path:[[round(k.co[0],1),round(k.co[1],1)] for k in f.keyframe_points] for f in ad.action.fcurves} if (ad and ad.action) else None})
bpy.ops.wm.save_mainfile()
rep["saved"]=True
print(json.dumps(rep,indent=1))
