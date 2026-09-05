import bpy, os, math
from mathutils import Vector
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
win = bpy.context.window; prev_scene = win.scene
src = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
tmp_scene = None; made=[]
try:
    src.frame_set(1434)
    tmp_scene = bpy.data.scenes.new("QA_TMP_SEAM")
    for n, col in (("X5_16_0.002", (0.15,0.75,1.0,1)), ("X5_61.002", (1.0,0.45,0.05,1))):
        o = src.objects[n]
        cp = o.copy()            # linked mesh copy, no data duplication
        cp.color = col
        tmp_scene.collection.objects.link(cp)
    emp = bpy.data.objects.new("QA_T", None); emp.location = Vector((0.0493,-0.315,0.5350))
    tmp_scene.collection.objects.link(emp)
    cd = bpy.data.cameras.new("QA_C"); cd.lens=60.0
    cam = bpy.data.objects.new("QA_C", cd); tmp_scene.collection.objects.link(cam)
    c = cam.constraints.new('TRACK_TO'); c.target = emp
    c.track_axis='TRACK_NEGATIVE_Z'; c.up_axis='UP_Y'
    tmp_scene.camera = cam
    r = tmp_scene.render
    r.engine='BLENDER_WORKBENCH'; r.resolution_x=r.resolution_y=760; r.resolution_percentage=100
    r.film_transparent = False
    sh = tmp_scene.display.shading
    sh.light='FLAT'; sh.color_type='OBJECT'; sh.show_object_outline=True
    sh.show_cavity = True
    win.scene = tmp_scene
    views=[]
    for az in (0,45,90,135,180,225,270,315):
        views.append(("seam_az%03d"%az, az, 6.0, 1.15))
    views += [("seam_el00_a30",30,0.0,0.42), ("seam_el00_a210",210,0.0,0.42),
              ("seam_el14_a75",75,14.0,0.34), ("seam_el14_a255",255,14.0,0.34)]
    TGT = emp.location
    for name, az, el, rad in views:
        a=math.radians(az); e=math.radians(el)
        cam.location = TGT + Vector((rad*math.cos(e)*math.cos(a), rad*math.cos(e)*math.sin(a), rad*math.sin(e)))
        r.filepath = os.path.join(OUT, "sm_%s.png"%name)
        bpy.ops.render.render(write_still=True)
        made.append(name)
    msg="ok: "+", ".join(made)
finally:
    win.scene = prev_scene
    if tmp_scene:
        objs = list(tmp_scene.collection.objects)
        for o in objs:
            d=o.data; bpy.data.objects.remove(o, do_unlink=True)
            if d is not None and d.users==0 and hasattr(d,'lens'): bpy.data.cameras.remove(d)
        bpy.data.scenes.remove(tmp_scene)
print(msg)
print("scenes now:", [s.name for s in bpy.data.scenes])
print("window scene:", bpy.context.window.scene.name)
