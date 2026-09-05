import bpy, json, math
from mathutils import Vector, Matrix
SC=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
rep={"targets":[],"notes":[]}

def key(id_data, path, index, kvs, interp='BEZIER', easing='AUTO'):
    for f,v in kvs:
        if index is None:
            if path.endswith("offset_factor"): id_data.constraints["Follow Path"].offset_factor=v
            elif "." in path: 
                head,tail=path.rsplit(".",1); setattr(id_data.path_resolve(head),tail,v)
            else: setattr(id_data,path,v)
            id_data.keyframe_insert(path, frame=f)
        else:
            cur=id_data.path_resolve(path); cur[index]=v
            id_data.keyframe_insert(path, index=index, frame=f)
    for fc in id_data.animation_data.action.fcurves:
        if fc.data_path==path and (index is None or fc.array_index==index):
            for kp in fc.keyframe_points:
                kp.interpolation=interp
                if interp not in ('CONSTANT','LINEAR'): kp.easing=easing
            fc.update()
def bez(P0,CC,P1,t):
    u=1-t
    return Vector(tuple(u*u*P0[i]+2*t*u*CC[i]+t*t*P1[i] for i in range(3)))
def arc_poly(P0,CC,P1,NOUT=200,NS=1200):
    pts=[bez(P0,CC,P1,i/(NS-1)) for i in range(NS)]
    L=[0.0]
    for i in range(1,NS): L.append(L[-1]+(pts[i]-pts[i-1]).length)
    tot=L[-1]; out=[]; j=0
    for k in range(NOUT):
        tg=tot*k/(NOUT-1)
        while j<NS-2 and L[j+1]<tg: j+=1
        seg=L[j+1]-L[j]; f=0.0 if seg<=0 else (tg-L[j])/seg
        out.append(pts[j].lerp(pts[j+1],f))
    return out,tot
def emat(name,color,strength):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    e=nt.nodes.new("ShaderNodeEmission"); o=nt.nodes.new("ShaderNodeOutputMaterial")
    e.inputs["Color"].default_value=(*color,1.0); e.inputs["Strength"].default_value=strength
    nt.links.new(e.outputs["Emission"], o.inputs["Surface"])
    return m
def fcv(o,path,idx,frame,default=0.0):
    ad=o.animation_data
    if not (ad and ad.action): return default
    for fc in ad.action.fcurves:
        if fc.data_path==path and fc.array_index==idx: return fc.evaluate(frame)
    return default

# ---- 1. strip the scale keys b2 put on the sleeves, restore base scale ----
BASE={"A":0.47244,"B":0.08663,"C":0.08836}
for k in "ABC":
    o=bpy.data.objects["P08_SLV_%s"%k]
    ad=o.animation_data
    if ad and ad.action:
        for fc in [f for f in ad.action.fcurves if f.data_path=='scale']:
            ad.action.fcurves.remove(fc)
    o.scale=(BASE[k],)*3
rep["notes"].append("sleeve scale fcurves removed, base scale restored")

col=bpy.data.collections["P08_SLVFX"]
TAPER=bpy.data.objects["P08_TRAIL_TAPER"]
DOTMESH=bpy.data.objects["P08_FXDOT_BLUE"].data
SPEC={
 "A":dict(O=Vector((0.0,471.0,0.35)),  bow=Vector((0,0,1)),            t0=2544, dotc=(0.55,0.75,1.0), trc=(0.25,0.55,1.0)),
 "B":dict(O=Vector((-0.85,470.0,-0.75)),bow=Vector((-0.882,0,-0.471)), t0=2550, dotc=(0.10,0.42,1.0), trc=(0.06,0.34,1.0)),
 "C":dict(O=Vector((0.85,470.0,-0.75)), bow=Vector((0.882,0,-0.472)),  t0=2556, dotc=(1.00,0.16,0.52),trc=(1.00,0.10,0.44)),
}
DOT_R_SCALE=1.25; BEVEL=0.09
for k,s in SPEC.items():
    piv=bpy.data.objects["P08_PIV_%s"%k]; slv=bpy.data.objects["P08_SLV_%s"%k]
    t0=s["t0"]; t1=t0+17; t2=t1+4; t3=t1+12
    # analytic world matrix of the sleeve at t1 (no depsgraph)
    ang=fcv(piv,'rotation_euler',2,t1,piv.rotation_euler[2])
    Pw=Matrix.Translation(piv.location) @ Matrix.Rotation(ang,4,'Z')
    W=Pw @ slv.matrix_parent_inverse @ slv.matrix_basis
    bb=[W@Vector(c) for c in slv.bound_box]
    ymax=max(p.y for p in bb); centre=piv.location.copy()
    T=Vector((centre.x, ymax+0.7, centre.z))     # just in front of the front face
    O=s["O"]; L=(T-O).length
    CC=(O+T)*0.5 + s["bow"]*(0.22*L) + Vector((0,0.15*L,0))
    pts,alen=arc_poly(O,CC,T)

    cob=bpy.data.objects["P08_SLVTRAIL_%s"%k]
    sp=cob.data.splines[0]
    for i,p in enumerate(pts): sp.points[i].co=(p.x,p.y,p.z,1.0)
    cob.data.update_tag()

    # ---- sleeve materialises by scaling its PIVOT (pivot sits on the visual centre) ----
    for ax in range(3):
        key(piv,'scale',ax,[(t1,0.10),(t1+7,1.06),(t1+12,1.0)],'SINE','EASE_OUT')
    rep["targets"].append({"k":k,"piv_ang_deg":round(math.degrees(ang),2),"ymax":round(ymax,2),
        "T":[round(v,2) for v in T],"CC":[round(v,2) for v in CC],"arc":round(alen,2),"frames":[t0,t1,t2,t3]})
    if piv.animation_data and piv.animation_data.action:
        piv.animation_data.action.name="ACT_P08_P08_PIV_%s"%k

bpy.ops.wm.save_mainfile()
rep["saved"]=True
print(json.dumps(rep,indent=1))
