import bpy, math
from mathutils import Vector, Matrix
src=bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
log=[]
try:
    win.scene=src; src.frame_set(1080)          # rest pose: MOTOR_SPIN rot_z == 0
    dg=bpy.context.evaluated_depsgraph_get()
    g8=src.objects["X5_8.002"]; ms=src.objects["X5_MOTOR_SPIN"]

    # ---- least-squares fit of the gear axis from its tooth-tip vertices ----
    oe=g8.evaluated_get(dg); mw=oe.matrix_world
    P=[mw@v.co for v in oe.data.vertices if 0.213 <= (mw@v.co).z <= 0.290]
    c0x=sum(p.x for p in P)/len(P); c0y=sum(p.y for p in P)/len(P)
    rmax=max(math.hypot(p.x-c0x,p.y-c0y) for p in P)
    tips=[p for p in P if math.hypot(p.x-c0x,p.y-c0y) > rmax*0.985]
    cx,cy=c0x,c0y
    for _ in range(40):                          # Kasa-style refinement
        rs=[math.hypot(p.x-cx,p.y-cy) for p in tips]
        rm=sum(rs)/len(rs)
        dx=sum((rm/r-1.0)*(cx-p.x) for p,r in zip(tips,rs))/len(tips)
        dy=sum((rm/r-1.0)*(cy-p.y) for p,r in zip(tips,rs))/len(tips)
        cx+=dx; cy+=dy
    rs=[math.hypot(p.x-cx,p.y-cy) for p in tips]
    log.append("gear axis fit: (%.5f, %.5f)  tip r %.5f +/- %.5f  (n=%d)" % (
        cx,cy,sum(rs)/len(rs),(max(rs)-min(rs))/2,len(tips)))
    log.append("centre distance to motor axis (%.4f,%.4f) = %.5f" % (ms.location.x,ms.location.y,
               math.hypot(cx-ms.location.x, cy-ms.location.y)))

    # ---- build the in-place spin pivot ----
    piv = bpy.data.objects.get("X5_GEAR_SPIN")
    if piv is None:
        piv = bpy.data.objects.new("X5_GEAR_SPIN", None)
        piv.empty_display_type='PLAIN_AXES'; piv.empty_display_size=0.06
    if piv.name not in src.collection.objects:
        src.collection.objects.link(piv)
    piv.parent=None
    piv.location=(cx, cy, ms.location.z)
    piv.rotation_euler=(0.0,0.0,0.0); piv.scale=(1,1,1)
    piv_rest = Matrix.Translation(Vector((cx,cy,ms.location.z)))

    # ---- re-parent the gear: orbit about the motor axis -> spin about its own axis ----
    old_basis = g8.matrix_basis.copy()
    ms_rest = Matrix.Translation(ms.location)          # rot 0 at frame 1080, scale 1
    world_rest = ms_rest @ g8.matrix_parent_inverse @ old_basis
    g8.parent = piv
    g8.matrix_parent_inverse = piv_rest.inverted()
    g8.matrix_basis = world_rest                        # so world == world_rest at spin 0
    log.append("X5_8.002 re-parented: X5_MOTOR_SPIN -> X5_GEAR_SPIN")
    log.append("  rest world loc = %s (canonical product transform)" % (
        tuple(round(v,5) for v in world_rest.translation),))

    # ---- driver: gear spins at -17/39 of the motor, exactly in sync ----
    piv.driver_remove("rotation_euler", 2)
    fc = piv.driver_add("rotation_euler", 2)
    d = fc.driver; d.type='SCRIPTED'
    var = d.variables.new(); var.name="m"; var.type='TRANSFORMS'
    t = var.targets[0]; t.id = ms; t.transform_type='ROT_Z'
    t.transform_space='WORLD_SPACE'; t.rotation_mode='AUTO'
    d.expression = "-m * 17.0 / 39.0"
    log.append("driver on X5_GEAR_SPIN.rotation_euler[2] = -m*17/39  (m = X5_MOTOR_SPIN rot Z)")
    log.append("MOTOR_SPIN children now: %s" % [c.name for c in ms.children])
finally:
    src.frame_set(1434); win.scene=prev
print("\n".join(log))
