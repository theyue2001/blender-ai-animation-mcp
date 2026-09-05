import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT = "D:/接案/26_0825_紅犀牛3D動畫/VScode/tmp/act3_logo"
L=[]
sc1 = bpy.data.scenes["01_SCN_OPENING_P01_P03"]
prev = bpy.context.window.scene
pfr = sc1.frame_current
try:
    bpy.context.window.scene = sc1
    sc1.frame_set(340)
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc1.camera
    names = ["16_0.002","40.002","32.002","38_0.002","P04_Silver_Bezel_34.002","49.002","61.002"]
    xs=[]; ys=[]
    for n in names:
        o = bpy.data.objects.get(n)
        if not o: continue
        oe = o.evaluated_get(dg); me = oe.to_mesh()
        for v in me.vertices:
            c = world_to_camera_view(sc1, cam, oe.matrix_world @ v.co)
            xs.append(c.x); ys.append(1-c.y)
        oe.to_mesh_clear()
    L.append("scene01 device ndc x=%.3f..%.3f y=%.3f..%.3f" % (min(xs),max(xs),min(ys),max(ys)))
    bx = (max(0.0,min(xs)-0.02), min(1.0,max(xs)+0.02))
    by = (max(0.0,1-(max(ys)+0.02)), min(1.0,1-(min(ys)-0.02)))
    L.append("border x=%s y=%s" % (bx,by))
    pe,pp = sc1.render.engine, sc1.render.resolution_percentage
    pb,pc,pf = sc1.render.use_border, sc1.render.use_crop_to_border, sc1.render.filepath
    pss = sc1.cycles.samples
    try:
        sc1.render.engine='CYCLES'; sc1.render.resolution_percentage=100
        sc1.render.use_border=True; sc1.render.use_crop_to_border=True
        sc1.render.border_min_x,sc1.render.border_max_x = bx
        sc1.render.border_min_y,sc1.render.border_max_y = by
        sc1.cycles.samples=96
        sc1.render.filepath = OUT + "/" + "ref_s01_device.png"
        bpy.ops.render.render(write_still=True)
        L.append("-> ref_s01_device.png")
    finally:
        sc1.render.engine, sc1.render.resolution_percentage = pe,pp
        sc1.render.use_border, sc1.render.use_crop_to_border, sc1.render.filepath = pb,pc,pf
        sc1.cycles.samples = pss
finally:
    sc1.frame_set(pfr); bpy.context.window.scene = prev
print("\n".join(L))
