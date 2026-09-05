import bpy, json, math
from mathutils import Vector
SC=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
rep={"created":[],"notes":[]}

# ---------- helpers ----------
def key(id_data, path, index, kvs, interp='BEZIER', easing='AUTO'):
    for f,v in kvs:
        if index is None:
            setattr_path(id_data, path, v); id_data.keyframe_insert(path, frame=f)
        else:
            cur=id_data.path_resolve(path); cur[index]=v
            id_data.keyframe_insert(path, index=index, frame=f)
    ad=id_data.animation_data
    for fc in ad.action.fcurves:
        if fc.data_path==path and (index is None or fc.array_index==index):
            for kp in fc.keyframe_points:
                kp.interpolation=interp
                if interp not in ('CONSTANT','LINEAR'): kp.easing=easing
            fc.update()
def setattr_path(o,path,v):
    if "." in path and "[" not in path.split(".")[0]:
        head,tail=path.rsplit(".",1); setattr(o.path_resolve(head), tail, v)
    elif path.endswith("offset_factor"):
        o.constraints["Follow Path"].offset_factor=v
    else:
        setattr(o,path,v)
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

# ---------- collection ----------
parent_col=bpy.data.collections["P08_SLEEVES"]
col=bpy.data.collections.get("P08_SLVFX")
if not col:
    col=bpy.data.collections.new("P08_SLVFX"); parent_col.children.link(col)

TAPER=bpy.data.objects["P08_TRAIL_TAPER"]
DOTMESH=bpy.data.objects["P08_FXDOT_BLUE"].data

SPEC={
 "A":dict(O=Vector((0.0,471.0,0.35)),  bow=Vector((0,0,1)),            t0=2544, dotc=(0.55,0.75,1.0), trc=(0.25,0.55,1.0)),
 "B":dict(O=Vector((-0.85,470.0,-0.75)),bow=Vector((-0.882,0,-0.471)), t0=2550, dotc=(0.10,0.42,1.0), trc=(0.06,0.34,1.0)),
 "C":dict(O=Vector((0.85,470.0,-0.75)), bow=Vector((0.882,0,-0.472)),  t0=2556, dotc=(1.00,0.16,0.52),trc=(1.00,0.10,0.44)),
}
DOT_R_SCALE=1.25          # mesh radius 0.24 -> 0.30
BEVEL=0.09
for k,s in SPEC.items():
    slv=bpy.data.objects["P08_SLV_%s"%k]
    T=slv.matrix_world.translation.copy()
    O=s["O"]
    L=(T-O).length
    CC=(O+T)*0.5 + s["bow"]*(0.22*L) + Vector((0,0.15*L,0))
    pts,alen=arc_poly(O,CC,T)
    t0=s["t0"]; t1=t0+17; t2=t1+4; t3=t1+12

    # ---- trail curve ----
    cn="P08_SLVTRAIL_%s"%k
    old=bpy.data.objects.get(cn)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    cu=bpy.data.curves.new(cn,'CURVE'); cu.dimensions='3D'; cu.resolution_u=1
    sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for i,p in enumerate(pts): sp.points[i].co=(p.x,p.y,p.z,1.0)
    cu.use_path=True; cu.bevel_depth=BEVEL; cu.bevel_resolution=4
    cu.taper_object=TAPER; cu.use_fill_caps=True
    cu.bevel_factor_start=0.0; cu.bevel_factor_end=0.0
    cob=bpy.data.objects.new(cn,cu); col.objects.link(cob)
    cob.data.materials.append(emat("MAT_P08_SLVFX_TRAIL_%s"%k, s["trc"], 14.0))
    key(cu,'bevel_factor_end',None,[(t0,0.0),(t1,1.0)],'CUBIC','EASE_OUT')
    key(cu,'bevel_factor_start',None,[(t0,0.0),(t1,0.45),(t3,1.0)],'SINE','EASE_IN_OUT')
    key(cob,'hide_render',None,[(2400,True),(t0,False),(t3+2,True)],'CONSTANT')
    key(cob,'hide_viewport',None,[(2400,True),(t0,False),(t3+2,True)],'CONSTANT')

    # ---- head dot ----
    dn="P08_SLVDOT_%s"%k
    old=bpy.data.objects.get(dn)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    dob=bpy.data.objects.new(dn, DOTMESH); col.objects.link(dob)
    dob.location=(0,0,0)
    if dob.material_slots:
        dob.material_slots[0].link='OBJECT'
        dob.material_slots[0].material=emat("MAT_P08_SLVFX_DOT_%s"%k, s["dotc"], 90.0)
    else:
        rep["notes"].append("no material slot on dot "+dn)
    c=dob.constraints.new('FOLLOW_PATH'); c.target=cob
    c.use_fixed_location=True; c.use_curve_follow=False; c.use_curve_radius=False
    c.forward_axis='FORWARD_Y'; c.up_axis='UP_Z'
    key(dob,'constraints["Follow Path"].offset_factor',None,[(t0,0.0),(t1,1.0)],'CUBIC','EASE_OUT')
    for ax in range(3):
        key(dob,'scale',ax,[(t0,DOT_R_SCALE*0.55),(t1,DOT_R_SCALE*1.0),(t2,DOT_R_SCALE*3.2),(t3,DOT_R_SCALE*0.001)],'SINE','EASE_IN_OUT')
    key(dob,'hide_render',None,[(2400,True),(t0,False),(t3+2,True)],'CONSTANT')
    key(dob,'hide_viewport',None,[(2400,True),(t0,False),(t3+2,True)],'CONSTANT')
    dm=dob.material_slots[0].material
    dm.node_tree.animation_data_create()
    for f,v in [(t0,70.0),(t1,95.0),(t2,430.0),(t3,0.0)]:
        dm.node_tree.nodes["Emission"].inputs["Strength"].default_value=v
        dm.node_tree.keyframe_insert('nodes["Emission"].inputs[1].default_value',frame=f)

    # ---- burst light riding the dot ----
    ln="LGT_P08_SLVFX_%s"%k
    old=bpy.data.objects.get(ln)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    ld=bpy.data.lights.new(ln,'POINT'); ld.shadow_soft_size=0.35
    ld.color=s["dotc"]
    lob=bpy.data.objects.new(ln,ld); col.objects.link(lob)
    lob.parent=dob; lob.matrix_parent_inverse.identity()
    lob.location=(0,3.0,0)      # +Y = toward camera, lights the front face
    key(ld,'energy',None,[(t0,0.0),(t1,600.0),(t2,4200.0),(t3,0.0)],'SINE','EASE_IN_OUT')

    # ---- sleeve materialise ----
    base=slv.scale[0]
    for ax in range(3):
        key(slv,'scale',ax,[(t1,base*0.10),(t1+7,base*1.06),(t1+12,base*1.0)],'SINE','EASE_OUT')
    ad=slv.animation_data
    for fc in ad.action.fcurves:
        if fc.data_path in ('hide_render','hide_viewport'):
            for kp in fc.keyframe_points:
                if abs(kp.co[0]-2538.0)<0.5:
                    kp.co[0]=float(t1); kp.handle_left[0]=float(t1)-1; kp.handle_right[0]=float(t1)+1
            fc.update()
    # tidy action names
    for holder,suffix in ((cob,cn),(dob,dn),(lob,ln)):
        if holder.animation_data and holder.animation_data.action:
            holder.animation_data.action.name="ACT_P08_"+suffix
    rep["created"].append({"k":k,"O":[round(v,2) for v in O],"CC":[round(v,2) for v in CC],
        "T":[round(v,2) for v in T],"arc_len":round(alen,2),"frames":[t0,t1,t2,t3],"base_scale":round(base,5)})

bpy.ops.wm.save_mainfile()
rep["saved"]=True
print(json.dumps(rep,indent=1))
