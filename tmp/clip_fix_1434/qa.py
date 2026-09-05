import bpy, os, math
from mathutils import Vector
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev_scene = win.scene
r = sc.render
P = dict(e=r.engine, rx=r.resolution_x, ry=r.resolution_y, pct=r.resolution_percentage,
         fp=r.filepath, cam=sc.camera)
TGT = Vector((0.0493, -0.315, 0.545))
tmp = []
try:
    win.scene = sc; sc.frame_set(1434)
    emp = bpy.data.objects.new("QA_TGT", None); emp.location = TGT
    sc.collection.objects.link(emp); tmp.append(emp)
    cd = bpy.data.cameras.new("QA_CAM"); cd.lens = 50.0
    cam = bpy.data.objects.new("QA_CAM", cd); sc.collection.objects.link(cam); tmp.append(cam)
    c = cam.constraints.new('TRACK_TO'); c.target = emp
    c.track_axis='TRACK_NEGATIVE_Z'; c.up_axis='UP_Y'
    r.engine='BLENDER_EEVEE_NEXT'; r.resolution_x=r.resolution_y=760; r.resolution_percentage=100
    sc.camera = cam
    views=[]
    for az in (0,45,90,135,180,225,270,315):
        views.append(("az%03d_el20"%az, az, 20.0, 0.52))
    views += [("top_el65", 30, 65.0, 0.50), ("low_el05", 200, 5.0, 0.50),
              ("tight_el15", 90, 15.0, 0.30), ("tight_el40", 270, 40.0, 0.30)]
    made=[]
    for name, az, el, rad in views:
        a = math.radians(az); e = math.radians(el)
        cam.location = TGT + Vector((rad*math.cos(e)*math.cos(a), rad*math.cos(e)*math.sin(a), rad*math.sin(e)))
        r.filepath = os.path.join(OUT, "qa_%s.png" % name)
        bpy.ops.render.render(write_still=True)
        made.append(name)
    msg = "rendered: " + ", ".join(made)
finally:
    r.engine=P['e']; r.resolution_x=P['rx']; r.resolution_y=P['ry']
    r.resolution_percentage=P['pct']; r.filepath=P['fp']; sc.camera=P['cam']
    for o in tmp:
        try:
            d = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if d and d.users == 0:
                (bpy.data.cameras if hasattr(d,'lens') else bpy.data.meshes).remove(d)
        except Exception as ex: pass
    win.scene = prev_scene
print(msg)
print("scene.camera restored to:", sc.camera.name)
print("QA objects left in scene:", [o.name for o in sc.objects if o.name.startswith("QA_")])
