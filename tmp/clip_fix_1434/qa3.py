import bpy, os, math, json
from mathutils import Vector
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
win = bpy.context.window; prev_scene = win.scene
src = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
me = bpy.data.objects["X5_16_0.002"].data
bk = json.load(open(os.path.join(OUT,"vert_backup.json")))["coords"]
moved = set(int(k) for k in bk)
fixed = {}
tmp_scene=None; log=[]
try:
    # ---- normal-change analysis (uses both states) ----
    faces = [p for p in me.polygons if any(v in moved for v in p.vertices)]
    n_after = {p.index: p.normal.copy() for p in faces}
    for k,co in bk.items():
        i=int(k); v=me.vertices[i]; fixed[i]=(v.co.x,v.co.y,v.co.z); v.co = co
    me.update()
    angs=[]
    for p in faces:
        a = p.normal; b = n_after[p.index]
        d = max(-1.0, min(1.0, a.normalized().dot(b.normalized())))
        angs.append(math.degrees(math.acos(d)))
    angs.sort()
    log.append("faces touched: %d" % len(faces))
    log.append("face-normal rotation caused by the edit: median %.3f deg  p95 %.3f  p99 %.3f  max %.3f" % (
        angs[len(angs)//2], angs[int(.95*len(angs))], angs[int(.99*len(angs))], angs[-1]))
    for t in (0.5,1.0,2.0,5.0):
        log.append("   faces rotated > %.1f deg: %d (%.2f%%)" % (t, sum(1 for a in angs if a>t),
                   100.0*sum(1 for a in angs if a>t)/len(angs)))
    # ---- BEFORE workbench renders (still reverted) ----
    tmp_scene = bpy.data.scenes.new("QA_TMP_B")
    for n,col in (("X5_16_0.002",(0.15,0.75,1.0,1)),("X5_61.002",(1.0,0.45,0.05,1))):
        cp = src.objects[n].copy(); cp.color=col; tmp_scene.collection.objects.link(cp)
    emp=bpy.data.objects.new("QB_T",None); emp.location=Vector((0.0493,-0.315,0.5350))
    tmp_scene.collection.objects.link(emp)
    cd=bpy.data.cameras.new("QB_C"); cd.lens=60.0
    cam=bpy.data.objects.new("QB_C",cd); tmp_scene.collection.objects.link(cam)
    c=cam.constraints.new('TRACK_TO'); c.target=emp; c.track_axis='TRACK_NEGATIVE_Z'; c.up_axis='UP_Y'
    tmp_scene.camera=cam
    r=tmp_scene.render; r.engine='BLENDER_WORKBENCH'; r.resolution_x=r.resolution_y=760; r.resolution_percentage=100
    sh=tmp_scene.display.shading; sh.light='FLAT'; sh.color_type='OBJECT'; sh.show_object_outline=True; sh.show_cavity=True
    win.scene = tmp_scene
    for az in (0,45,90,135,180,225,270,315):
        a=math.radians(az); e=math.radians(6.0)
        cam.location = emp.location + Vector((1.15*math.cos(e)*math.cos(a),1.15*math.cos(e)*math.sin(a),1.15*math.sin(e)))
        r.filepath=os.path.join(OUT,"smb_seam_az%03d.png"%az)
        bpy.ops.render.render(write_still=True)
    log.append("before-state workbench renders done")
finally:
    win.scene = prev_scene
    if tmp_scene:
        for o in list(tmp_scene.collection.objects):
            d=o.data; bpy.data.objects.remove(o,do_unlink=True)
            if d is not None and d.users==0 and hasattr(d,'lens'): bpy.data.cameras.remove(d)
        bpy.data.scenes.remove(tmp_scene)
    for i,(x,y,z) in fixed.items(): me.vertices[i].co=(x,y,z)
    me.update()
    log.append("fix re-applied to %d verts" % len(fixed))
print("\n".join(log))
