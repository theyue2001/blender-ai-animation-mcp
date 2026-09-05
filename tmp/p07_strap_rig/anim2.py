import bpy, math
from mathutils import Vector, Quaternion
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
log = []

# Reference grammar taken from the client's clips (dreamina 1412 / 2637 / 3393):
# the camera HUGS the webbing, travels forward along it at speed, turns with the
# belt, and decelerates into a macro on the cam-lock where the strap feeds
# through.  It never shows the whole product.
#
# (frame, s along belt, outward clearance, z offset, look-ahead in s, lens, fstop)
CAM = [(1632, 0.400, 0.170, 0.050, 0.080, 24.0, 4.0),
       (1824, 0.450, 0.165, 0.050, 0.078, 24.0, 4.0),
       (1872, 0.600, 0.155, 0.050, 0.072, 24.0, 4.0),
       (1908, 0.720, 0.150, 0.050, 0.065, 26.0, 4.0),
       (1944, 0.820, 0.165, 0.052, 0.055, 28.0, 4.0),
       (1980, 0.885, 0.230, 0.062, 0.040, 34.0, 4.0),
       (2016, 0.912, 0.340, 0.080, 0.030, 42.0, 4.0),
       (2160, 0.918, 0.360, 0.082, 0.028, 42.0, 4.0)]

prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc
    cuo = bpy.data.objects["CRV_StrapUpper_Path"]

    def curve_now():
        """Sample the belt as it actually is on the current frame, so the stated
        clearance is a real clearance even while the loop is slack."""
        dg = bpy.context.evaluated_depsgraph_get()
        ev = cuo.evaluated_get(dg); tm = ev.to_mesh()
        dn = [cuo.matrix_world @ v.co.copy() for v in tm.vertices]
        ev.to_mesh_clear()
        dl = [0.0]
        for j in range(1, len(dn)):
            dl.append(dl[-1] + (dn[j] - dn[j - 1]).length)
        return dn, dl

    def at(dn, dl, s):
        t = max(0.0, min(1.0, s)) * dl[-1]
        lo, hi = 0, len(dl) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if dl[m] <= t:
                lo = m
            else:
                hi = m
        d = dl[hi] - dl[lo]
        return dn[lo].lerp(dn[hi], 0.0 if d < 1e-12 else (t - dl[lo]) / d)

    cam = bpy.data.objects.get("P07_SHOT_CAM")
    if cam is None:
        cd = bpy.data.cameras.new("P07_SHOT_CAM")
        cam = bpy.data.objects.new("P07_SHOT_CAM", cd)
        sc.collection.objects.link(cam)
    cam.rotation_mode = 'QUATERNION'
    cam.data.clip_start = 0.004
    cam.data.clip_end = 200.0
    for holder in (cam, cam.data):
        if holder.animation_data and holder.animation_data.action:
            a = holder.animation_data.action
            holder.animation_data.action = None
            a.use_fake_user = False
            bpy.data.actions.remove(a)
    sc.camera = cam

    lastq = None
    rows = []
    for fr, s, dist, hgt, ahead, lens, fstop in CAM:
        sc.frame_set(fr)
        dn, dl = curve_now()
        CB = ((min(p.x for p in dn) + max(p.x for p in dn)) * 0.5,
              (min(p.y for p in dn) + max(p.y for p in dn)) * 0.5)
        p = at(dn, dl, s)
        r = Vector((p.x - CB[0], p.y - CB[1], 0.0)).normalized()
        pos = p + r * dist + Vector((0, 0, hgt))
        tgt = at(dn, dl, min(1.0, s + ahead))
        q = (tgt - pos).normalized().to_track_quat('-Z', 'Z')
        if lastq is not None and q.dot(lastq) < 0.0:
            q = Quaternion((-q.w, -q.x, -q.y, -q.z))
        lastq = q
        cam.location = pos
        cam.rotation_quaternion = q
        cam.data.lens = lens
        cam.data.dof.use_dof = True
        cam.data.dof.focus_distance = (tgt - pos).length
        cam.data.dof.aperture_fstop = fstop
        cam.keyframe_insert("location", frame=fr)
        cam.keyframe_insert("rotation_quaternion", frame=fr)
        cam.data.keyframe_insert("lens", frame=fr)
        cam.data.dof.keyframe_insert("focus_distance", frame=fr)
        cam.data.dof.keyframe_insert("aperture_fstop", frame=fr)
        rows.append("  f%-5d s=%.3f pos=(%+.3f,%+.3f,%+.3f) aim=(%+.3f,%+.3f,%+.3f) d=%.3f lens=%.0f"
                    % (fr, s, pos.x, pos.y, pos.z, tgt.x, tgt.y, tgt.z, (tgt - pos).length, lens))
    for src in (cam.animation_data.action, cam.data.animation_data.action):
        for fc in src.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
    log.append("P07_SHOT_CAM rebuilt to reference grammar (hug the webbing -> macro on the cam-lock):")
    log += rows
    sc.frame_set(1824)
    bpy.ops.wm.save_mainfile()
    log.append("saved in place: %s" % bpy.data.filepath)
finally:
    bpy.context.window.scene = prev
print("\n".join(log))
