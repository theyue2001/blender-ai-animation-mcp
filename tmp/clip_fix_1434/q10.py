import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
try:
    win.scene = sc; sc.frame_set(1434)
    for n in ["X5_16_0.002","X5_61.002","X5_56.002","X5_62.002"]:
        o = sc.objects[n]; me = o.data
        users = [ob.name for ob in bpy.data.objects if ob.data is me]
        scns = sorted({s.name for s in bpy.data.scenes for ob in s.objects if ob.data is me})
        print("%-22s mesh=%-20s users=%d  objs=%s" % (n, me.name, me.users, users))
        print("       in scenes: %s" % scns)
        print("       shade_smooth(first poly)=%s  has_custom_normals=%s  modifiers=%s  scale=%s" % (
            me.polygons[0].use_smooth, me.has_custom_normals,
            [(m.name,m.type) for m in o.modifiers], tuple(round(v,4) for v in o.scale)))
        try:
            print("       auto_smooth_angle=%.3f use_auto_smooth=%s" % (me.auto_smooth_angle, me.use_auto_smooth))
        except AttributeError:
            print("       (4.1+: auto smooth is a modifier)")
        sm = sum(1 for p in me.polygons if p.use_smooth)
        print("       smooth polys %d / %d" % (sm, len(me.polygons)))
finally:
    win.scene = prev
