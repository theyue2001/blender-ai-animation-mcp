import bpy, math
from mathutils import Vector
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]; vl = sc.view_layers[0]
SB = [0.0, 0.048, 0.13, 0.25, 0.38, 0.51, 0.63, 0.74, 0.845, 0.925, 1.0]
out = []
prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc
    sc.frame_set(1)
    for tag, C in (("StrapUpper", (0.0589, -2.1837)), ("StrapLower", (0.0455, -2.3473))):
        cuo = bpy.data.objects["CRV_" + tag + "_Path"]
        ao = bpy.data.objects["NITE_" + tag + "_Armature"]
        ob = bpy.data.objects["P07_" + tag.replace("Strap", "STRAP_").upper().replace("STRAP_UPPER", "STRAP_UPPER").replace("STRAP_LOWER", "STRAP_LOWER")]
        for bp in cuo.data.splines[0].bezier_points:
            bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
        cuo.data.resolution_u = 64
        dg = bpy.context.evaluated_depsgraph_get()
        ev = cuo.evaluated_get(dg); me = ev.to_mesh()
        pts = [v.co.copy() for v in me.vertices]     # curve local space
        ev.to_mesh_clear()
        dl = [0.0]
        for i in range(1, len(pts)):
            dl.append(dl[-1] + (pts[i] - pts[i - 1]).length)
        L = dl[-1]

        def on_curve(f):
            t = max(0.0, min(1.0, f)) * L
            lo, hi = 0, len(dl) - 1
            while hi - lo > 1:
                k = (lo + hi) // 2
                if dl[k] <= t:
                    lo = k
                else:
                    hi = k
            d = dl[hi] - dl[lo]
            g = 0.0 if d < 1e-12 else (t - dl[lo]) / d
            return pts[lo].lerp(pts[hi], g)

        W = ao.matrix_world.copy(); Wi = W.inverted()
        upl = (Wi.to_3x3() @ Vector((0, 0, 1))).normalized()
        joints = [on_curve(s) for s in SB]
        vl.objects.active = ao
        bpy.ops.object.mode_set(mode='EDIT')
        for i in range(len(SB) - 1):
            d = ao.data.edit_bones["DEF_%s_%02d" % (tag, i)]
            d.head = joints[i]; d.tail = joints[i + 1]
            d.align_roll(upl)
        bpy.ops.object.mode_set(mode='OBJECT')
        out.append("%s: repositioned 10 deform bones on AUTO curve (curveL=%.4f world, samples=%d)"
                   % (tag, L * W.to_scale()[0], len(pts)))
finally:
    bpy.context.window.scene = prev
print("\n".join(out))
