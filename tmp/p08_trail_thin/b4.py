import bpy, json, math
from mathutils import Vector, Matrix
rep={"fixed":[]}
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
def retime(id_data, path, idx, mapping, interp='SINE', easing='EASE_IN_OUT'):
    """replace an existing fcurve's keys with [(frame,value),...]"""
    ad=id_data.animation_data
    for fc in list(ad.action.fcurves):
        if fc.data_path==path and (idx is None or fc.array_index==idx):
            ad.action.fcurves.remove(fc)
    for f,v in mapping:
        if path.endswith("offset_factor"): id_data.constraints["Follow Path"].offset_factor=v
        elif idx is None and "." in path:
            head,tail=path.rsplit(".",1); setattr(id_data.path_resolve(head),tail,v)
        elif idx is None: setattr(id_data,path,v)
        else:
            cur=id_data.path_resolve(path); cur[idx]=v
        id_data.keyframe_insert(path, index=(-1 if idx is None else idx), frame=f)
    for fc in ad.action.fcurves:
        if fc.data_path==path and (idx is None or fc.array_index==idx):
            for kp in fc.keyframe_points:
                kp.interpolation=interp
                if interp not in ('CONSTANT','LINEAR'): kp.easing=easing
            fc.update()

SPEC={
 "A":dict(O=Vector((0.0,471.0,0.35)),   rad=Vector((0,0,1)),            t0=2544),
 "B":dict(O=Vector((-0.85,470.0,-0.75)),rad=Vector((-0.882,0,-0.471)),  t0=2550),
 "C":dict(O=Vector((0.85,470.0,-0.75)), rad=Vector((0.882,0,-0.472)),   t0=2556),
}
DOT_R_SCALE=1.25
for k,s in SPEC.items():
    piv=bpy.data.objects["P08_PIV_%s"%k]
    cob=bpy.data.objects["P08_SLVTRAIL_%s"%k]
    dob=bpy.data.objects["P08_SLVDOT_%s"%k]
    lob=bpy.data.objects["LGT_P08_SLVFX_%s"%k]
    t0=s["t0"]; t1=t0+17; t2=t1+3; t3=t1+9
    # --- rebuild path with a TANGENTIAL bow so the arc is visible on screen ---
    sp=cob.data.splines[0]
    T=Vector(sp.points[-1].co[:3]); O=s["O"]; L=(T-O).length
    r=s["rad"]; tan=Vector((r.z,0.0,-r.x)).normalized()
    CC=(O+T)*0.5 + tan*(0.22*L) + r*(0.08*L) + Vector((0,0.15*L,0))
    pts,alen=arc_poly(O,CC,T)
    for i,p in enumerate(pts): sp.points[i].co=(p.x,p.y,p.z,1.0)
    cob.data.bevel_depth=0.11
    cob.data.update_tag()
    # --- tame the bloom ---
    retime(cob.data,'bevel_factor_start',None,[(t0,0.0),(t1,0.45),(t3,1.0)])
    for ax in range(3):
        retime(dob,'scale',ax,[(t0,DOT_R_SCALE*0.55),(t1,DOT_R_SCALE*1.0),
                               (t2,DOT_R_SCALE*1.9),(t3,DOT_R_SCALE*0.001)])
    dm=dob.material_slots[0].material
    retime(dm.node_tree,'nodes["Emission"].inputs[1].default_value',None,
           [(t0,70.0),(t1,95.0),(t2,200.0),(t3,0.0)])
    retime(lob.data,'energy',None,[(t0,0.0),(t1,600.0),(t2,2200.0),(t3,0.0)])
    retime(dob,'hide_render',None,[(2400,True),(t0,False),(t3+2,True)],'CONSTANT')
    retime(dob,'hide_viewport',None,[(2400,True),(t0,False),(t3+2,True)],'CONSTANT')
    retime(cob,'hide_render',None,[(2400,True),(t0,False),(t3+2,True)],'CONSTANT')
    retime(cob,'hide_viewport',None,[(2400,True),(t0,False),(t3+2,True)],'CONSTANT')
    # sleeve growth ends sooner so it is on screen while the flash is still lit
    for ax in range(3):
        retime(piv,'scale',ax,[(t1,0.10),(t1+6,1.06),(t1+11,1.0)],'SINE','EASE_OUT')
    # screen-space chord of the bow, as a sanity number
    mid=bez(O,CC,T,0.5)
    rep["fixed"].append({"k":k,"CC":[round(v,2) for v in CC],"arc":round(alen,2),
                         "bow_tangential":round((0.22*L),2),"frames":[t0,t1,t2,t3]})
bpy.ops.wm.save_mainfile()
rep["saved"]=True
print(json.dumps(rep,indent=1))
