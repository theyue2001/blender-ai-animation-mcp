import bpy, math
from mathutils import Vector, Quaternion
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
log = []

# ---------------------------------------------------------------------------
# Reference grammar, measured across all six clips:
#   - the CAMERA carries the motion; the belt is essentially rigid
#   - the whole product is never visible; the subject is always a fragment
#   - standoff 0.6-0.7 band widths, frame height 2.2-2.7 band widths
#     -> only possible on a WIDE prime (18-20mm), which is why 28-45mm at the
#        same standoff read as a blurred slab
#   - the aim point is ALSO offset outward from the belt; aiming straight at
#     the centreline points the lens into the loop void
#   - lengthwise travel, fast then decelerating, cut between fixed primes
# ---------------------------------------------------------------------------

# The belt holds a slight slack through shots A and B (no visible change, as in
# the references) and only seats during the locked-off hero, so the storyboard
# "belt joins / feeds through the buckle" beat survives at reference scale.
AMPS = [(1632, 0.35, 0.35),
        (1824, 0.35, 0.35),
        (1944, 0.35, 0.35),
        (1968, 0.22, 0.20),
        (1992, 0.06, 0.05),
        (2008, -0.02, 0.00),
        (2016, 0.00, 0.00),
        (2160, 0.00, 0.00)]

# ('belt', frame, s, clearance, z, look-ahead, aim-clearance, aim-z, lens, fstop)
# ('fixed', frame, pos, aim, lens, fstop)
# Standoff pulled back from the reference's 0.6-0.7 band widths: those clips
# sell the extreme close-up on WOVEN texture, which this CAD strap does not
# have.  At 0.15 it renders as a featureless pale wall; at 0.45-0.55 the
# silhouette and the raking specular carry the read instead.
# aim-clearance is a small ABSOLUTE offset (~0.06), not a fraction of the
# standoff - scaling it with the larger standoff throws the belt out of frame.
SHOT_A = [('belt', 1824, 0.250, 0.560, 0.080, 0.075, 0.065, 0.012, 24.0, 5.6),
          ('belt', 1841, 0.470, 0.540, 0.078, 0.072, 0.063, 0.012, 24.0, 5.6),
          ('belt', 1866, 0.560, 0.515, 0.074, 0.070, 0.060, 0.011, 24.0, 5.6),
          ('belt', 1893, 0.620, 0.495, 0.072, 0.068, 0.058, 0.011, 24.0, 5.6)]
SHOT_B = [('belt', 1894, 0.660, 0.470, 0.068, 0.062, 0.056, 0.010, 28.0, 5.0),
          ('belt', 1916, 0.760, 0.440, 0.064, 0.054, 0.052, 0.010, 28.0, 5.0),
          ('belt', 1938, 0.840, 0.410, 0.060, 0.044, 0.048, 0.009, 28.0, 4.5),
          ('belt', 1955, 0.880, 0.390, 0.056, 0.036, 0.045, 0.009, 28.0, 4.5)]
SHOT_C = [('fixed', 1956, (0.660, -0.760, 1.205), (0.288, -1.540, 1.008), 50.0, 4.0),
          ('fixed', 1991, (0.618, -0.792, 1.188), (0.284, -1.542, 1.006), 50.0, 4.0),
          ('fixed', 2016, (0.606, -0.802, 1.183), (0.283, -1.542, 1.006), 50.0, 4.0),
          ('fixed', 2160, (0.606, -0.802, 1.183), (0.283, -1.542, 1.006), 50.0, 4.0)]
CUTS = (1893, 1955)   # last frame of each block -> CONSTANT, so the next key jumps


def ss(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def bump(s, c, w):
    x = (s - c) / w
    return math.exp(-x * x) if abs(x) < 3.0 else 0.0


prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc

    # ---------------- belt ------------------------------------------------
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
        RAD = [Vector((p.x - C[0], p.y - C[1], 0.0)).normalized() for p in Pw]
        if ao.animation_data and ao.animation_data.action:
            ao.animation_data.action = None
        for nm in ("P07_SHOT_" + tag, "P07_SHOT_" + tag + ".001"):
            st = bpy.data.actions.get(nm)
            if st:
                st.use_fake_user = False
                bpy.data.actions.remove(st)
        act = bpy.data.actions.new("P07_SHOT_" + tag)
        if not ao.animation_data:
            ao.animation_data_create()
        ao.animation_data.action = act
        for fr, ab, aw in AMPS:
            for i in range(NCP):
                s = S[i]
                tap = 1.0 - ss((s - 0.860) / 0.050)
                dr = ab * gain * 0.075 * bump(s, 0.855, 0.030) * tap
                dz = ab * gain * 0.020 * bump(s, 0.855, 0.030) * tap
                dr += aw * gain * 0.085 * ss((s - 0.08) / 0.16) * (1.0 - ss((s - 0.74) / 0.12))
                dr += aw * gain * (0.055 * bump(s, 0.62, 0.09) +
                                   0.045 * bump(s, 0.35, 0.10) +
                                   0.035 * bump(s, 0.48, 0.07))
                dz += aw * gain * (0.030 * bump(s, 0.62, 0.09) -
                                   0.022 * bump(s, 0.35, 0.10))
                t = Pw[i] + RAD[i] * dr + Vector((0, 0, dz))
                pb = ao.pose.bones["%s_CP_%02d" % (tag, i)]
                pb.location = pb.bone.matrix_local.to_3x3().inverted() @ (Wi.to_3x3() @ (t - Pw[i]))
                pb.keyframe_insert("location", frame=fr)
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
        log.append("%s: %d CPs keyed %s (belt static through A/B, seats during C)"
                   % (tag, NCP, [a[0] for a in AMPS]))

    # ---------------- camera ----------------------------------------------
    cuo = bpy.data.objects["CRV_StrapUpper_Path"]

    def curve_now():
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

    rows = []
    lastq = None
    for row in SHOT_A + SHOT_B + SHOT_C:
        kind = row[0]; fr = row[1]
        sc.frame_set(fr)
        if kind == 'belt':
            s, clr, h, look, clra, ha, lens, fstop = row[2:]
            dn, dl = curve_now()
            CB = ((min(p.x for p in dn) + max(p.x for p in dn)) * 0.5,
                  (min(p.y for p in dn) + max(p.y for p in dn)) * 0.5)
            p = at(dn, dl, s)
            r = Vector((p.x - CB[0], p.y - CB[1], 0.0)).normalized()
            pos = p + r * clr + Vector((0, 0, h))
            sa = min(1.0, s + look)
            pa = at(dn, dl, sa)
            ra = Vector((pa.x - CB[0], pa.y - CB[1], 0.0)).normalized()
            tgt = pa + ra * clra + Vector((0, 0, ha))
        else:
            pos = Vector(row[2]); tgt = Vector(row[3]); lens = row[4]; fstop = row[5]
            s = -1.0
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
        rows.append("  %-5s f%-5d s=%6.3f pos=(%+.3f,%+.3f,%+.3f) aim=(%+.3f,%+.3f,%+.3f) d=%.3f %.0fmm f/%.1f"
                    % (kind, fr, s, pos.x, pos.y, pos.z, tgt.x, tgt.y, tgt.z,
                       (tgt - pos).length, lens, fstop))
    for src in (cam.animation_data.action, cam.data.animation_data.action):
        for fc in src.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
            # hard cut: hold the block's last value, then jump on the next key
            for kp in fc.keyframe_points:
                if int(round(kp.co[0])) in CUTS:
                    kp.interpolation = 'CONSTANT'
    log.append("P07_SHOT_CAM: 3 set-ups, hard cuts at %s, fixed primes 18/20/50mm" % (CUTS,))
    log += rows
    sc.frame_set(1824)
    bpy.ops.wm.save_mainfile()
    log.append("saved in place: %s" % bpy.data.filepath)
finally:
    bpy.context.window.scene = prev
print("\n".join(log))
