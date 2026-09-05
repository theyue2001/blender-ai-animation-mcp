import bpy, math
from mathutils import Vector, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
log = []

CTLS = ["ROOT", "SIDE_A", "BACK_A", "BACK_B", "MID", "BACK_C", "SIDE_B", "BUCKLE", "ENTRY", "END"]
SS = [0.0, 0.10, 0.22, 0.34, 0.46, 0.58, 0.70, 0.815, 0.905, 1.0]
FR = {"REST": 1, "A_STRAIGHT": 40, "B_CURVED": 80, "C_WAIST": 120, "D_BUCKLE": 160}

SPECS = [dict(tag="StrapUpper", C=(0.0589, -2.1837)),
         dict(tag="StrapLower", C=(0.0455, -2.3473))]

for S in SPECS:
    tag = S["tag"]; C = S["C"]
    ao = bpy.data.objects["NITE_" + tag + "_Armature"]
    cuo = bpy.data.objects["CRV_" + tag + "_Path"]
    W = ao.matrix_world.copy(); Wi = W.inverted()
    bps = cuo.data.splines[0].bezier_points
    Pw = [W @ bps[i].co.copy() for i in range(len(bps))]
    # curve length in world
    L = 0.0
    for i in range(1, len(Pw)):
        L += (Pw[i] - Pw[i - 1]).length
    L *= 1.02
    R = Pw[0]
    RAD = []
    for p in Pw:
        d = Vector((p.x - C[0], p.y - C[1], 0.0))
        RAD.append(d.normalized() if d.length > 1e-6 else Vector((0, 1, 0)))
    Dstr = Vector((0.25, 1.0, 0.0)).normalized()
    side = Vector((1.0, 0.0, 0.0))

    targets = {}
    targets["REST"] = [p.copy() for p in Pw]
    # A: straight
    targets["A_STRAIGHT"] = [R + Dstr * (SS[i] * L) for i in range(len(Pw))]
    # B: curved - a wide horizontal arc leaving the root
    Rc = L / math.pi
    tb = []
    for i in range(len(Pw)):
        th = SS[i] * math.pi * 0.85
        tb.append(R + Dstr * (Rc * math.sin(th)) + side * (Rc * (1 - math.cos(th))))
    targets["B_CURVED"] = tb
    # C: wrapped on the waist with a loose free end
    off_c = {"SIDE_B": (0.10, 0.02), "BUCKLE": (0.30, 0.06), "ENTRY": (0.55, 0.20), "END": (0.80, 0.35)}
    tc = []
    for i, nm in enumerate(CTLS):
        o = off_c.get(nm, (0.0, 0.0))
        tc.append(Pw[i] + RAD[i] * o[0] + Vector((0, 0, o[1])))
    targets["C_WAIST"] = tc
    # D: free end brought back in line with the buckle mouth
    off_d = {"SIDE_B": (0.02, 0.0), "BUCKLE": (0.05, 0.01), "ENTRY": (0.14, 0.05), "END": (0.22, 0.09)}
    td = []
    for i, nm in enumerate(CTLS):
        o = off_d.get(nm, (0.0, 0.0))
        td.append(Pw[i] + RAD[i] * o[0] + Vector((0, 0, o[1])))
    targets["D_BUCKLE"] = td

    if ao.animation_data and ao.animation_data.action:
        ao.animation_data.action = None
    act = bpy.data.actions.get("P07_TESTPOSES_" + tag)
    if act:
        bpy.data.actions.remove(act)
    for key, fr in sorted(FR.items(), key=lambda kv: kv[1]):
        tg = targets[key]
        for i, nm in enumerate(CTLS):
            bn = "%s_%s_CTRL" % (tag, nm)
            pb = ao.pose.bones[bn]
            delta_w = tg[i] - Pw[i]
            delta_a = Wi.to_3x3() @ delta_w
            M3 = pb.bone.matrix_local.to_3x3()
            pb.location = M3.inverted() @ delta_a
            pb.keyframe_insert("location", frame=fr)
    ao.animation_data.action.name = "P07_TESTPOSES_" + tag
    for fc in ao.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    log.append("%s: action=%s fcurves=%d frames=%s curveL=%.3f" %
               (tag, ao.animation_data.action.name, len(ao.animation_data.action.fcurves),
                sorted(FR.values()), L / 1.02))

sc.frame_start = 1; sc.frame_end = 200; sc.frame_current = 1
print("\n".join(log))
