import bpy, math
from mathutils import Vector, Quaternion, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
log = []

# Camera grammar from the client's clips (dreamina 1412 / 2637 / 3393):
# hug the webbing, travel forward along it, turn with the belt, decelerate into
# a macro on the cam-lock.  Distance chosen so the band reads as a ribbon
# crossing frame (about a third of frame height), not a blurred slab.
# (frame, s, outward clearance, z offset, look-ahead in s, lens, fstop)
# Two kinds of key.  'belt' keys hug the webbing (s, clearance, z, look-ahead);
# 'fixed' keys are explicit world pos/aim, used once the move swings out in
# front of the cam-lock for the macro - hugging the belt there only looks into
# the unlit inner face.
CAM = [('belt',  1632, 0.400, 0.62, 0.10, 0.075, 30.0, 8.0),
       ('belt',  1824, 0.450, 0.60, 0.10, 0.075, 30.0, 8.0),
       ('belt',  1872, 0.600, 0.56, 0.09, 0.070, 30.0, 8.0),
       ('belt',  1908, 0.720, 0.52, 0.09, 0.062, 32.0, 7.1),
       ('belt',  1944, 0.820, 0.50, 0.10, 0.052, 35.0, 6.3),
       ('fixed', 1980, (1.05, -1.02, 1.20), (0.44, -1.55, 1.010), 42.0, 5.6),
       ('fixed', 2016, (0.62, -0.72, 1.20), (0.30, -1.530, 1.020), 52.0, 5.0),
       ('fixed', 2160, (0.58, -0.76, 1.18), (0.29, -1.530, 1.020), 52.0, 5.0)]

prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc

    # ---- look: reference clips are near-black with a raking specular --------
    bg = [n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND'][0]
    bg.inputs['Color'].default_value = (0.006, 0.006, 0.007, 1.0)
    bpy.data.objects["P07_KEY"].data.energy = 1400.0
    bpy.data.objects["P07_FILL"].data.energy = 340.0
    log.append("world bg -> 0.006 ; KEY 2000->1400 ; FILL 800->260")

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

    # ---- travelling rake light rigid to the camera -------------------------
    rk = bpy.data.objects.get("P07_SHOT_RAKE")
    if rk is None:
        ld = bpy.data.lights.new("P07_SHOT_RAKE", 'AREA')
        rk = bpy.data.objects.new("P07_SHOT_RAKE", ld)
        sc.collection.objects.link(rk)
    rk.data.type = 'AREA'
    rk.data.shape = 'RECTANGLE'
    rk.data.size = 1.6
    rk.data.size_y = 0.25
    rk.data.energy = 260.0
    rk.parent = cam
    rk.location = (0.55, 0.30, 0.10)
    rk.rotation_euler = (math.radians(72), 0.0, math.radians(46))
    log.append("P07_SHOT_RAKE area light parented to the camera (rakes the weave)")

    lastq = None
    rows = []
    for row in CAM:
        kind = row[0]; fr = row[1]
        sc.frame_set(fr)
        if kind == 'belt':
            s, dist, hgt, ahead, lens, fstop = row[2:]
            dn, dl = curve_now()
            CB = ((min(p.x for p in dn) + max(p.x for p in dn)) * 0.5,
                  (min(p.y for p in dn) + max(p.y for p in dn)) * 0.5)
            p = at(dn, dl, s)
            r = Vector((p.x - CB[0], p.y - CB[1], 0.0)).normalized()
            pos = p + r * dist + Vector((0, 0, hgt))
            tgt = at(dn, dl, min(1.0, s + ahead))
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
        rows.append("  %-5s f%-5d s=%6.3f pos=(%+.3f,%+.3f,%+.3f) aim=(%+.3f,%+.3f,%+.3f) d=%.3f lens=%.0f f/%.1f"
                    % (kind, fr, s, pos.x, pos.y, pos.z, tgt.x, tgt.y, tgt.z, (tgt - pos).length, lens, fstop))
    for src in (cam.animation_data.action, cam.data.animation_data.action):
        for fc in src.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
    log.append("P07_SHOT_CAM rebuilt:")
    log += rows
    sc.frame_set(1824)
    bpy.ops.wm.save_mainfile()
    log.append("saved in place: %s" % bpy.data.filepath)
finally:
    bpy.context.window.scene = prev
print("\n".join(log))
