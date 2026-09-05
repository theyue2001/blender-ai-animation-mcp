import bpy
from mathutils import Vector
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
out=[]
out.append("frame range %d-%d  fps=%d  camera=%s"%(sc.frame_start,sc.frame_end,sc.render.fps,sc.camera.name if sc.camera else None))
out.append("markers: %s"%[(m.frame,m.name) for m in sorted(sc.timeline_markers,key=lambda m:m.frame)])
out.append("")
out.append("animated objects in scene:")
for o in sorted(sc.objects,key=lambda x:x.name):
    ad=o.animation_data
    if ad and ad.action:
        fr=[]
        for fc in ad.action.fcurves:
            for k in fc.keyframe_points: fr.append(k.co[0])
        out.append("  %-28s %-28s keys %d  frames %.0f..%.0f"%(o.name,ad.action.name,len(fr),min(fr),max(fr)))
    elif o.type=='CAMERA':
        out.append("  %-28s (camera, no anim) loc=%s"%(o.name,tuple(round(v,3) for v in o.location)))
out.append("")
out.append("upper strap curve: world position at key s values")
cuo=bpy.data.objects["CRV_StrapUpper_Path"]; W=cuo.matrix_world
dg=bpy.context.evaluated_depsgraph_get(); ev=cuo.evaluated_get(dg); tm=ev.to_mesh()
dn=[W@v.co.copy() for v in tm.vertices]; ev.to_mesh_clear()
dl=[0.0]
for j in range(1,len(dn)): dl.append(dl[-1]+(dn[j]-dn[j-1]).length)
L=dl[-1]
def at(s):
    t=s*L; lo,hi=0,len(dl)-1
    while hi-lo>1:
        m=(lo+hi)//2
        if dl[m]<=t: lo=m
        else: hi=m
    d=dl[hi]-dl[lo]
    return dn[lo].lerp(dn[hi],0.0 if d<1e-12 else (t-dl[lo])/d)
for s in (0.0,0.04,0.073,0.30,0.50,0.75,0.90,0.912,0.94,0.953,0.98,0.995,1.0):
    p=at(s); out.append("   s=%.3f  (%+.3f,%+.3f,%+.3f)"%(s,p.x,p.y,p.z))
out.append("   curve world length=%.4f"%L)
out.append("")
ao=bpy.data.objects["NITE_StrapUpper_Armature"]
out.append("upper CP bones=%d  CTRL=%s"%(sum(1 for b in ao.data.bones if "_CP_" in b.name),
          [b.name for b in ao.data.bones if b.name.endswith("_CTRL")]))
out.append("rig root empty at %s"%(tuple(round(v,4) for v in bpy.data.objects["NITE_Strap_Rig_ROOT"].location),))
print("\n".join(out))
