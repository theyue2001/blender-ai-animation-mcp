import bpy, json, math
from mathutils import Vector, Matrix
P=json.load(open(r"C:\Users\mountain\AppData\Local\Temp\claude\d-----26-0825----3D---VScode\87e289ce-469b-4c17-8671-68b6cfdb67b0\scratchpad\ring_params.json"))
C0=Vector(P["C0"]); R=P["R"]; DP={k:Vector(v) for k,v in P["DP"].items()}
D_END=P["D_END"]; D_START=P["D_START"]; camX=P["camX"]; camZ=P["camZ"]; RING_MAX=P["RING_MAX"]
TOCAM=Vector((0,1,0)); DOT_MAX=16.5
rep={}

def setval(owner,path,index,v):
    if index is None:
        head,_,attr=path.rpartition('.')
        tgt=owner.path_resolve(head) if head else owner
        setattr(tgt,attr,v)
    else:
        owner.path_resolve(path)[index]=v
def key(owner,path,index,fv,interp='BEZIER',easing='AUTO'):
    for f,v in fv:
        setval(owner,path,index,v)
        owner.keyframe_insert(data_path=path,index=(-1 if index is None else index),frame=f)
    ad=owner.animation_data
    for fc in ad.action.fcurves:
        if fc.data_path==path and (index is None or fc.array_index==index):
            for kp in fc.keyframe_points:
                kp.interpolation=interp; kp.easing=easing
            fc.update()

TIM={"A":dict(d0=2546,d1=2562,s0=2550,s1=2570),
     "C":dict(d0=2549,d1=2565,s0=2553,s1=2573),
     "B":dict(d0=2552,d1=2568,s0=2556,s1=2576)}
SETTLED=2578; F_END=2663; F_CUT=2669

for k in "ABC":
    t=TIM[k]; d=DP[k].normalized()
    e2=(TOCAM-d*TOCAM.dot(d)).normalized(); e3=d.cross(e2)
    piv=bpy.data.objects["P08_PIV_%s"%k]
    slv=bpy.data.objects["P08_SLV_%s"%k]
    tr =bpy.data.objects["P08_SLVTRAIL_%s"%k]
    dot=bpy.data.objects["P08_SLVDOT_%s"%k]
    lgt=bpy.data.objects["LGT_P08_SLVFX_%s"%k]
    for o in (piv,slv,tr,dot,lgt):
        if o.animation_data: o.animation_data_clear()
        if getattr(o.data,"animation_data",None): o.data.animation_data_clear()

    # ---- trail: radial ray from the array centre, slight tangential bow ----
    tr.matrix_world=Matrix.Identity(4)
    sp=tr.data.splines[0]; N=len(sp.points)
    for i,pt in enumerate(sp.points):
        u=i/(N-1.0)
        w=C0+d*(DOT_MAX*u)+e3*(0.09*DOT_MAX*math.sin(math.pi*u))
        pt.co=(w.x,w.y,w.z,1.0)
    tr.data.update_tag()
    key(tr.data,'bevel_factor_end',None,[(t["d0"],0.0),(t["d1"],1.0)],'CUBIC','EASE_OUT')
    key(tr.data,'bevel_factor_start',None,[(t["d0"],0.0),(t["d1"],0.45),(t["d1"]+10,1.0)],'BEZIER')
    key(tr,'hide_render',None,[(2400,True),(t["d0"],False),(t["d1"]+13,True)],'CONSTANT')
    key(tr,'hide_viewport',None,[(2400,True),(t["d0"],False),(t["d1"]+13,True)],'CONSTANT')

    # ---- dot rides the ray ----
    dot.location=(0,0,0)
    key(dot,'constraints["Follow Path"].offset_factor',None,
        [(t["d0"],0.0),(t["d1"],1.0)],'CUBIC','EASE_OUT')
    key(dot,'scale',0,[(t["d0"],0.5),(t["d1"],1.0),(t["d1"]+4,2.6),(t["d1"]+11,0.001)],'BEZIER')
    for ax in (1,2):
        key(dot,'scale',ax,[(t["d0"],0.5),(t["d1"],1.0),(t["d1"]+4,2.6),(t["d1"]+11,0.001)],'BEZIER')
    key(dot,'hide_render',None,[(2400,True),(t["d0"],False),(t["d1"]+13,True)],'CONSTANT')
    key(dot,'hide_viewport',None,[(2400,True),(t["d0"],False),(t["d1"]+13,True)],'CONSTANT')
    dm=dot.material_slots[0].material
    key(dm.node_tree,'nodes["Emission"].inputs[1].default_value',None,
        [(t["d0"],70.0),(t["d1"],95.0),(t["d1"]+4,430.0),(t["d1"]+11,0.0)],'BEZIER')

    # ---- burst light ----
    key(lgt.data,'energy',None,
        [(t["d0"],0.0),(t["d1"],500.0),(t["d1"]+4,3200.0),(t["d1"]+11,0.0)],'BEZIER')

    # ---- sleeve shoots out along the same ray ----
    key(piv,'location',0,[(t["s0"],(d*0.6).x),(t["s1"],(d*R).x)],'CUBIC','EASE_OUT')
    key(piv,'location',1,[(t["s0"],(d*0.6).y),(t["s1"],(d*R).y)],'CUBIC','EASE_OUT')
    key(piv,'location',2,[(t["s0"],(d*0.6).z),(t["s1"],(d*R).z)],'CUBIC','EASE_OUT')
    mid=t["s0"]+int(0.55*(t["s1"]-t["s0"]))
    for ax in (0,1,2):
        key(piv,'scale',ax,[(t["s0"],0.25),(mid,1.06),(t["s1"],1.0)],'BEZIER')
    key(slv,'hide_render',None,[(2320,True),(t["s0"],False),(F_CUT,True)],'CONSTANT')
    key(slv,'hide_viewport',None,[(2320,True),(t["s0"],False),(F_CUT,True)],'CONSTANT')
    rep.setdefault("timing",{})[k]=t

# ---- ring array rotation ----
ctr=bpy.data.objects["P08_RING_CTR"]
if ctr.animation_data: ctr.animation_data_clear()
ctr.rotation_mode='XYZ'
key(ctr,'rotation_euler',1,[(SETTLED,0.0),(F_END,RING_MAX)],'SINE','EASE_IN_OUT')

# ---- camera dolly ----
cam=bpy.data.objects["CAM_P08_02_Sleeves"]
if cam.animation_data: cam.animation_data_clear()
if cam.data.animation_data: cam.data.animation_data_clear()
cam.rotation_euler=(math.radians(90),0,math.radians(180))
key(cam,'location',0,[(2544,camX),(F_END,camX)],'BEZIER')
key(cam,'location',1,[(2544,C0.y+D_START),(F_END,C0.y+D_END)],'SINE','EASE_IN_OUT')
key(cam,'location',2,[(2544,camZ),(F_END,camZ)],'BEZIER')
key(cam.data,'dof.focus_distance',None,[(2544,D_START),(F_END,D_END)],'SINE','EASE_IN_OUT')
cam.data.lens=35.0

bpy.ops.wm.save_mainfile()
rep["ring_deg"]=round(math.degrees(RING_MAX),1)
rep["cam"]={"D_start":round(D_START,2),"D_end":round(D_END,2)}
rep["saved"]=True
print(json.dumps(rep,indent=1))
