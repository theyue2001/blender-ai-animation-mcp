import bpy, math
from mathutils import Vector, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
log = []
FR = {"REST": 1, "A_STRAIGHT": 40, "B_CURVED": 80, "C_WAIST": 120, "D_BUCKLE": 160, "REST_END": 200}


def ss(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


for tag in ("StrapUpper", "StrapLower"):
    ao = bpy.data.objects["NITE_" + tag + "_Armature"]
    cuo = bpy.data.objects["CRV_" + tag + "_Path"]
    W = ao.matrix_world.copy(); Wi = W.inverted()
    bps = cuo.data.splines[0].bezier_points
    NCP = len(bps)
    Pw = [W @ bps[i].co.copy() for i in range(NCP)]
    S = [i / (NCP - 1.0) for i in range(NCP)]
    L = sum((Pw[i] - Pw[i - 1]).length for i in range(1, NCP)) * 1.02
    C = ((min(p.x for p in Pw) + max(p.x for p in Pw)) * 0.5,
         (min(p.y for p in Pw) + max(p.y for p in Pw)) * 0.5)
    RAD = []
    for p in Pw:
        d = Vector((p.x - C[0], p.y - C[1], 0.0))
        RAD.append(d.normalized() if d.length > 1e-6 else Vector((0, 1, 0)))
    R = Pw[0]
    Dstr = Vector((0.25, 1.0, 0.0)).normalized()
    side = Vector((1.0, 0.0, 0.0))
    Rc = L / math.pi

    tg = {}
    tg["REST"] = [p.copy() for p in Pw]
    tg["REST_END"] = [p.copy() for p in Pw]
    tg["A_STRAIGHT"] = [R + Dstr * (S[i] * L) for i in range(NCP)]
    tg["B_CURVED"] = [R + Dstr * (Rc * math.sin(S[i] * math.pi * 0.85)) +
                      side * (Rc * (1 - math.cos(S[i] * math.pi * 0.85))) for i in range(NCP)]
    tg["C_WAIST"] = [Pw[i] + RAD[i] * (0.80 * ss((S[i] - 0.66) / 0.34)) +
                     Vector((0, 0, 0.35 * ss((S[i] - 0.66) / 0.34))) for i in range(NCP)]
    tg["D_BUCKLE"] = [Pw[i] + RAD[i] * (0.22 * ss((S[i] - 0.70) / 0.30)) +
                      Vector((0, 0, 0.09 * ss((S[i] - 0.70) / 0.30))) for i in range(NCP)]

    if ao.animation_data and ao.animation_data.action:
        ao.animation_data.action = None
    old = bpy.data.actions.get("P07_TESTPOSES_" + tag)
    if old:
        bpy.data.actions.remove(old)
    for key, fr in sorted(FR.items(), key=lambda kv: kv[1]):
        t = tg[key]
        for i in range(NCP):
            pb = ao.pose.bones["%s_CP_%02d" % (tag, i)]
            delta = Wi.to_3x3() @ (t[i] - Pw[i])
            pb.location = pb.bone.matrix_local.to_3x3().inverted() @ delta
            pb.keyframe_insert("location", frame=fr)
    ao.animation_data.action.name = "P07_TESTPOSES_" + tag
    for fc in ao.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    log.append("%s: %d CP bones keyed at frames %s (action %s)" %
               (tag, NCP, sorted(FR.values()), ao.animation_data.action.name))


print("\n".join(log))
