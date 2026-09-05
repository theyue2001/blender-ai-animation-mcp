import bpy, os, math
from mathutils import Vector
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
win=bpy.context.window; prev=win.scene
src=bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
tmp=None
try:
    print("=== MOTOR_SPIN rig ===")
    ms=src.objects["X5_MOTOR_SPIN"]
    print("  X5_MOTOR_SPIN loc=%s rot=%s children=%s" % (
        tuple(round(v,4) for v in ms.location), tuple(round(math.degrees(v),2) for v in ms.rotation_euler),
        [c.name for c in ms.children]))
    ad=ms.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            ks=[(round(k.co[0]),round(math.degrees(k.co[1]),1)) for k in fc.keyframe_points]
            print("    fcurve %s[%d] keys=%s" % (fc.data_path, fc.array_index, ks[:6]))
    for f in (1080,1434):
        src.frame_set(f)
        dg=bpy.context.evaluated_depsgraph_get()
        e=ms.evaluated_get(dg)
        print("  frame %d MOTOR_SPIN world rot Z = %.2f deg" % (f, math.degrees(e.matrix_world.to_euler().z)))
    # geometry of the parts, relative to the motor axis
    src.frame_set(1080)
    dg=bpy.context.evaluated_depsgraph_get()
    AX,AY=0.0493,-0.3201
    print("=== part footprint about the motor axis (at rest, frame 1080) ===")
    for n in ["X5_4.002","X5_6.002","X5_8.002","X5_12.002","X5_1.002","X5_2.002","X5_10.002"]:
        o=src.objects[n].evaluated_get(dg); me=o.data; mwo=o.matrix_world
        rs=[]; zs=[]
        step=max(1,len(me.vertices)//4000)
        for i in range(0,len(me.vertices),step):
            p=mwo@me.vertices[i].co
            rs.append(math.hypot(p.x-AX,p.y-AY)); zs.append(p.z)
        print("   %-12s r %.4f..%.4f   z %.4f..%.4f   parent=%s" % (
            n.replace("X5_",""), min(rs),max(rs),min(zs),max(zs), src.objects[n].parent.name if src.objects[n].parent else "-"))
finally:
    src.frame_set(1434); win.scene=prev
