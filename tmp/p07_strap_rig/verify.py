import bpy, sys
SN="05_SCN_P07_STRAP_RIG"
print("FILE:", bpy.data.filepath)
if SN not in bpy.data.scenes:
    print("!! scene missing"); sys.exit()
sc=bpy.data.scenes[SN]
print("scene range %d-%d fps=%d camera=%s"%(sc.frame_start,sc.frame_end,sc.render.fps,
      sc.camera.name if sc.camera else None))
print("markers:", [(m.frame,m.name) for m in sorted(sc.timeline_markers,key=lambda m:m.frame)])
print("--- rig ---")
for tag,obn in (("StrapUpper","P07_STRAP_UPPER"),("StrapLower","P07_STRAP_LOWER")):
    ao=bpy.data.objects.get("NITE_%s_Armature"%tag)
    cu=bpy.data.objects.get("CRV_%s_Path"%tag)
    ob=bpy.data.objects.get(obn)
    if not (ao and cu and ob): print("!! missing",tag); continue
    ik=[(c.type,c.target.name,c.chain_count) for pb in ao.pose.bones for c in pb.constraints]
    print("%-11s bones=%d DEF=%d CP=%d CTRL=%d | curve %d pts %d hooks | mesh %d v, %d vg, mods=%s | IK=%s"%(
        tag,len(ao.data.bones),sum(1 for b in ao.data.bones if b.use_deform),
        sum(1 for b in ao.data.bones if "_CP_" in b.name),
        sum(1 for b in ao.data.bones if b.name.endswith("_CTRL")),
        len(cu.data.splines[0].bezier_points),len([m for m in cu.modifiers if m.type=='HOOK']),
        len(ob.data.vertices),len(ob.vertex_groups),[m.type for m in ob.modifiers],ik))
    print("            CTRL:",[b.name for b in ao.data.bones if b.name.endswith("_CTRL")])
print("--- animation ---")
for o in sc.objects:
    ad=o.animation_data
    if ad and ad.action:
        f=[k.co[0] for fc in ad.action.fcurves for k in fc.keyframe_points]
        print("  %-24s %-24s %4d keys  %.0f..%.0f"%(o.name,ad.action.name,len(f),min(f),max(f)))
    if o.type=='CAMERA':
        print("  %-24s lens=%.1f dof=%s loc=%s"%(o.name,o.data.lens,o.data.dof.use_dof,
              tuple(round(v,3) for v in o.location)))
        if o.data.animation_data and o.data.animation_data.action:
            f=[k.co[0] for fc in o.data.animation_data.action.fcurves for k in fc.keyframe_points]
            print("        lens/dof action %d keys %.0f..%.0f"%(len(f),min(f),max(f)))
print("P07 actions:",[a.name for a in bpy.data.actions if a.name.startswith("P07_")])
print("--- originals untouched ---")
for nm in ("64.002","65.002","59.002","60.002"):
    o=bpy.data.objects.get(nm)
    print("  %-9s mods=%d vgroups=%d action=%s"%(nm,len(o.modifiers),len(o.vertex_groups),
          bool(o.animation_data and o.animation_data.action)))
print("scenes in file:",[s.name for s in bpy.data.scenes])
