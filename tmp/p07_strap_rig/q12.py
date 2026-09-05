import bpy, math
from mathutils import Vector
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
out = []


def measure(nm):
    ob = bpy.data.objects[nm]
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    pts = [ob.matrix_world @ v.co.copy() for v in me.vertices]
    ev.to_mesh_clear()
    # order: curve tessellation is sequential
    turns = []
    for i in range(1, len(pts) - 1):
        a = pts[i] - pts[i - 1]; b = pts[i + 1] - pts[i]
        if a.length < 1e-9 or b.length < 1e-9:
            continue
        ang = a.normalized().angle(b.normalized())
        seg = (a.length + b.length) * 0.5
        turns.append(math.degrees(ang) / max(seg, 1e-9))
    sign = 0
    for i in range(1, len(pts) - 1):
        pass
    # oscillation: count local maxima of curvature (a smooth arc has very few)
    peaks = 0
    for i in range(1, len(turns) - 1):
        if turns[i] > turns[i - 1] and turns[i] > turns[i + 1] and turns[i] > 5.0:
            peaks += 1
    return len(pts), max(turns) if turns else 0, sum(turns) / len(turns) if turns else 0, peaks


prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc
    for nm in ("CRV_StrapUpper_Path", "CRV_StrapLower_Path"):
        cu = bpy.data.objects[nm].data
        bps = cu.splines[0].bezier_points
        saved = [(bp.co.copy(), bp.handle_left.copy(), bp.handle_right.copy()) for bp in bps]
        for fr in (1, 80):
            sc.frame_set(fr)
            n, mx, av, pk = measure(nm)
            out.append("%s FREE  f%-3d pts=%d maxCurv=%.1f avgCurv=%.2f curvPeaks=%d" % (nm, fr, n, mx, av, pk))
        for bp in bps:
            bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
        cu.splines[0].bezier_points[0].handle_left_type = 'AUTO'
        for fr in (1, 80):
            sc.frame_set(fr)
            n, mx, av, pk = measure(nm)
            out.append("%s AUTO  f%-3d pts=%d maxCurv=%.1f avgCurv=%.2f curvPeaks=%d" % (nm, fr, n, mx, av, pk))
        # how far did AUTO move the rest curve from the FREE (fitted) one?
        sc.frame_set(1)
        d = max((saved[i][0] - bps[i].co).length for i in range(len(bps)))
        hd = max(max((saved[i][1] - bps[i].handle_left).length, (saved[i][2] - bps[i].handle_right).length) for i in range(len(bps)))
        out.append("   AUTO vs FREE: co moved max %.5f (local), handles moved max %.3f (local)" % (d, hd))
    sc.frame_set(1)
finally:
    bpy.context.window.scene = prev
print("\n".join(out))
