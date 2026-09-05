import bpy, math
from mathutils import Vector, Quaternion
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
log = []

# ---- shot map (24 fps) ------------------------------------------------------
F_HOLD = 1632   # 1:08  assembly holds the slack state while it rotates in
F_IN = 1824     # 1:16  mechanism beat starts
F_OUT = 2016    # 1:24  belt locked, hands free
F_END = 2160    # 1:30

# The free tail is captured by the cam-lock, so it must not be lifted out of
# the housing.  Slack sits just upstream of the buckle and around the loop, and
# is drawn out through the lock as the belt tightens.
AMPS = [(F_HOLD, 1.00, 1.00),
        (F_IN,   1.00, 1.00),
        (1872,   0.72, 0.95),
        (1908,   0.40, 0.80),
        (1944,   0.12, 0.45),
        (1980,  -0.03, 0.12),
        (2004,   0.010, 0.0),
        (F_OUT,  0.00, 0.00),
        (F_END,  0.00, 0.00)]

# push in from the whole belt+device assembly onto the 59.002 cam-lock
# (frame, camera position, aim point, lens)
CAM = [(F_HOLD, (1.45, -0.35, 1.75), (0.160, -1.850, 1.000), 35.0),
       (F_IN,   (1.45, -0.35, 1.75), (0.160, -1.850, 1.000), 35.0),
       (1872,   (1.22, -0.42, 1.64), (0.200, -1.720, 1.010), 38.0),
       (1920,   (1.02, -0.48, 1.55), (0.240, -1.620, 1.010), 42.0),
       (1968,   (0.92, -0.52, 1.50), (0.260, -1.560, 1.015), 44.0),
       (F_OUT,  (0.86, -0.56, 1.47), (0.267, -1.518, 1.017), 45.0),
       (F_END,  (0.80, -0.60, 1.44), (0.267, -1.518, 1.017), 45.0)]


def ss(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def bump(s, c, w):
    x = (s - c) / w
    return math.exp(-x * x) if abs(x) < 3.0 else 0.0


prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc

    # ---- belt ---------------------------------------------------------------
    for tag, gain in (("StrapUpper", 1.0), ("StrapLower", 0.40)):
        ao = bpy.data.objects["NITE_" + tag + "_Armature"]
        cuo = bpy.data.objects["CRV_" + tag + "_Path"]
        W = ao.matrix_world.copy(); Wi = W.inverted()
        bps = cuo.data.splines[0].bezier_points
        NCP = len(bps)
        Pw = [W @ bps[i].co.copy() for i in range(NCP)]
        S = [i / (NCP - 1.0) for i in range(NCP)]
        C = ((min(p.x for p in Pw) + max(p.x for p in Pw)) * 0.5,
             (min(p.y for p in Pw) + max(p.y for p in Pw)) * 0.5)
        RAD = []
        for p in Pw:
            d = Vector((p.x - C[0], p.y - C[1], 0.0))
            RAD.append(d.normalized() if d.length > 1e-6 else Vector((0, 1, 0)))

        old = ao.animation_data.action if ao.animation_data else None
        if old:
            old.use_fake_user = True
            ao.animation_data.action = None
        for nm in ("P07_SHOT_" + tag, "P07_SHOT_" + tag + ".001",
                   "P07_SHOT_" + tag + ".002", "P07_SHOT_" + tag + ".003"):
            stale = bpy.data.actions.get(nm)
            if stale:
                stale.use_fake_user = False
                bpy.data.actions.remove(stale)
        act = bpy.data.actions.new("P07_SHOT_" + tag)
        if not ao.animation_data:
            ao.animation_data_create()
        ao.animation_data.action = act

        for fr, ab, aw in AMPS:
            for i in range(NCP):
                s = S[i]
                # slack held just before the buckle, forced to zero before the
                # cam-lock at s=0.912 so the strap never enters the housing
                tap = 1.0 - ss((s - 0.860) / 0.050)
                dr = ab * gain * 0.075 * bump(s, 0.855, 0.030) * tap
                dz = ab * gain * 0.020 * bump(s, 0.855, 0.030) * tap
                # the whole loop runs slack and is drawn in as it tightens,
                # tapered to nothing at both pieces of hardware
                dr += aw * gain * 0.085 * ss((s - 0.08) / 0.16) * (1.0 - ss((s - 0.74) / 0.12))
                # slack waves around the loop, taken up as tension propagates
                dr += aw * gain * (0.055 * bump(s, 0.62, 0.09) +
                                   0.045 * bump(s, 0.35, 0.10) +
                                   0.035 * bump(s, 0.48, 0.07))
                dz += aw * gain * (0.030 * bump(s, 0.62, 0.09) -
                                   0.022 * bump(s, 0.35, 0.10))
                t = Pw[i] + RAD[i] * dr + Vector((0, 0, dz))
                pb = ao.pose.bones["%s_CP_%02d" % (tag, i)]
                delta = Wi.to_3x3() @ (t - Pw[i])
                pb.location = pb.bone.matrix_local.to_3x3().inverted() @ delta
                pb.keyframe_insert("location", frame=fr)
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
        log.append("%s: %d CP bones keyed at %s (action %s)" %
                   (tag, NCP, [a[0] for a in AMPS], act.name))

    # ---- camera: travel along the strap into the cam-lock --------------------
    cuo = bpy.data.objects["CRV_StrapUpper_Path"]
    Wc = cuo.matrix_world
    dg = bpy.context.evaluated_depsgraph_get()
    ev = cuo.evaluated_get(dg); tm = ev.to_mesh()
    dn = [Wc @ v.co.copy() for v in tm.vertices]
    ev.to_mesh_clear()
    dl = [0.0]
    for j in range(1, len(dn)):
        dl.append(dl[-1] + (dn[j] - dn[j - 1]).length)
    LC = dl[-1]

    def on(s):
        t = max(0.0, min(1.0, s)) * LC
        lo, hi = 0, len(dl) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if dl[m] <= t:
                lo = m
            else:
                hi = m
        d = dl[hi] - dl[lo]
        return dn[lo].lerp(dn[hi], 0.0 if d < 1e-12 else (t - dl[lo]) / d)

    CB = ((min(p.x for p in dn) + max(p.x for p in dn)) * 0.5,
          (min(p.y for p in dn) + max(p.y for p in dn)) * 0.5)

    cam = bpy.data.objects.get("P07_SHOT_CAM")
    if cam is None:
        cd = bpy.data.cameras.new("P07_SHOT_CAM")
        cam = bpy.data.objects.new("P07_SHOT_CAM", cd)
        sc.collection.objects.link(cam)
    cam.data.clip_start = 0.005
    cam.data.clip_end = 200.0
    cam.rotation_mode = 'QUATERNION'
    if cam.animation_data and cam.animation_data.action:
        bpy.data.actions.remove(cam.animation_data.action)
    sc.camera = cam

    lastq = None
    for fr, pos, tgt, lens in CAM:
        pos = Vector(pos); tgt = Vector(tgt)
        q = (tgt - pos).normalized().to_track_quat('-Z', 'Z')
        if lastq is not None and q.dot(lastq) < 0.0:
            q = Quaternion((-q.w, -q.x, -q.y, -q.z))
        lastq = q
        cam.location = pos
        cam.rotation_quaternion = q
        cam.data.lens = lens
        cam.data.dof.use_dof = True
        cam.data.dof.focus_distance = (tgt - pos).length
        cam.data.dof.aperture_fstop = 4.5
        cam.keyframe_insert("location", frame=fr)
        cam.keyframe_insert("rotation_quaternion", frame=fr)
        cam.data.keyframe_insert("lens", frame=fr)
        cam.data.dof.keyframe_insert("focus_distance", frame=fr)
    for src in (cam.animation_data.action, cam.data.animation_data.action):
        for fc in src.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
    log.append("P07_SHOT_CAM keyed at %s ; scene camera set" % [c[0] for c in CAM])

    sc.frame_set(F_IN)
    bpy.ops.wm.save_mainfile()
    log.append("saved in place: %s" % bpy.data.filepath)
finally:
    bpy.context.window.scene = prev
print("\n".join(log))
