import bpy, os, math
from mathutils import Vector
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
win=bpy.context.window; prev=win.scene
src=bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
tmp=None
try:
    tmp=bpy.data.scenes.new("QA_MOTOR")
    tmp.frame_start, tmp.frame_end = 1080, 1800
    cols={"X5_1.002":(0.20,0.45,0.95,1),"X5_8.002":(1.0,0.40,0.05,1),
          "X5_4.002":(0.20,0.90,0.35,1),"X5_2.002":(0.75,0.75,0.78,1),"X5_12.002":(0.9,0.2,0.8,1)}
    for n,c in cols.items():
        o=src.objects[n]; cp=o.copy(); cp.color=c
        if o.parent:                       # bake the world transform, keep the rig out of it
            cp.parent=None; cp.matrix_world=o.matrix_world.copy()
        tmp.collection.objects.link(cp)
    emp=bpy.data.objects.new("QM_T",None); emp.location=Vector((0.0493,-0.3201,0.24))
    tmp.collection.objects.link(emp)
    cd=bpy.data.cameras.new("QM_C"); cd.lens=55.0
    cam=bpy.data.objects.new("QM_C",cd); tmp.collection.objects.link(cam)
    c=cam.constraints.new('TRACK_TO'); c.target=emp; c.track_axis='TRACK_NEGATIVE_Z'; c.up_axis='UP_Y'
    tmp.camera=cam
    r=tmp.render; r.engine='BLENDER_WORKBENCH'; r.resolution_x=r.resolution_y=800; r.resolution_percentage=100
    s=tmp.display.shading; s.light='STUDIO'; s.color_type='OBJECT'; s.show_object_outline=True; s.show_cavity=True
    win.scene=tmp
    for nm,(az,el,rad) in {"top":(0,89,1.15),"sideX":(0,8,1.15),"q45":(45,25,1.15),"q315":(315,25,1.15)}.items():
        a=math.radians(az); e=math.radians(el)
        cam.location = emp.location + Vector((rad*math.cos(e)*math.cos(a),rad*math.cos(e)*math.sin(a),rad*math.sin(e)))
        r.filepath=os.path.join(OUT,"mot_%s.png"%nm)
        bpy.ops.render.render(write_still=True)
    msg="ok"
finally:
    win.scene=prev
    if tmp:
        for o in list(tmp.collection.objects):
            d=o.data; bpy.data.objects.remove(o,do_unlink=True)
            if d is not None and d.users==0 and hasattr(d,'lens'): bpy.data.cameras.remove(d)
        bpy.data.scenes.remove(tmp)
print(msg, "| blue=1.002 body  orange=8.002  green=4.002  grey=2.002  magenta=12.002")
