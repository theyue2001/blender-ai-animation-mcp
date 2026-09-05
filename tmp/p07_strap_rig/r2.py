import bpy, math
from mathutils import Vector, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
cam = bpy.data.objects["P07_QA_CAM"]
OUT = "d:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p07_strap_rig/"
OUT = bpy.path.abspath(OUT)


def look(eye, tgt):
    e = Vector(eye); t = Vector(tgt)
    d = (t - e).normalized()
    up = Vector((0, 0, 1))
    if abs(d.dot(up)) > 0.999:
        up = Vector((0, 1, 0))
    r = d.cross(up).normalized(); u = r.cross(d).normalized()
    cam.matrix_world = Matrix(((r.x, u.x, -d.x, e.x), (r.y, u.y, -d.y, e.y),
                               (r.z, u.z, -d.z, e.z), (0, 0, 0, 1)))


JOBS = [
    (1824, "SB_1_16_q34",   (2.6, 0.9, 2.2),    (0.05, -2.2, 0.7),  55),
    (1824, "SB_1_16_buckle",(0.05, 0.35, 1.02), (0.05, -1.5, 1.0),  95),
    (2016, "SB_1_24_q34",   (2.6, 0.9, 2.2),    (0.05, -2.2, 0.7),  55),
]

prev = bpy.context.window.scene
prevf = {s.name: s.frame_current for s in bpy.data.scenes}
try:
    bpy.context.window.scene = sc
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x = 960; sc.render.resolution_y = 960
    for fr, name, eye, tgt, lens in JOBS:
        sc.frame_set(fr)
        cam.data.lens = lens
        look(eye, tgt)
        sc.render.filepath = OUT + "p_" + name + ".png"
        bpy.ops.render.render(write_still=True)
    sc.frame_set(1)
finally:
    bpy.context.window.scene = prev
    for s in bpy.data.scenes:
        s.frame_current = prevf[s.name]
print("rendered %d frames to %s" % (len(JOBS), OUT))
