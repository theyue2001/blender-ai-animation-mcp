import bpy, json, math
from mathutils import Vector
rep={}
# --- per-mesh local profile: which local axis is the bore, and which end is the dome ---
for k in "ABC":
    o=bpy.data.objects["P08_SLV_%s"%k]
    me=o.data
    vs=[v.co for v in me.vertices]
    n=len(vs)
    mn=Vector((min(v[i] for v in vs) for i in range(3)))
    mx=Vector((max(v[i] for v in vs) for i in range(3)))
    ext=mx-mn
    axis=max(range(3),key=lambda i:ext[i])          # local long axis
    a,b=[i for i in range(3) if i!=axis]
    # radius profile along the long axis, 10 slabs
    lo,hi=mn[axis],mx[axis]; L=hi-lo
    prof=[]
    for s in range(10):
        y0=lo+L*s/10.0; y1=lo+L*(s+1)/10.0
        rs=[math.hypot(v[a],v[b]) for v in vs if y0<=v[axis]<y1]
        prof.append(round(max(rs),3) if rs else 0.0)
    rep["mesh_%s"%k]={"verts":n,"local_min":[round(v,3) for v in mn],"local_max":[round(v,3) for v in mx],
        "ext":[round(v,3) for v in ext],"long_axis":"XYZ"[axis],
        "bbox_centre_local":[round((mn[i]+mx[i])/2,4) for i in range(3)],
        "radius_profile_lo_to_hi":prof,
        "dome_end":"+"+"XYZ"[axis] if sum(prof[6:])>sum(prof[:4]) else "-"+"XYZ"[axis]}
# --- current parenting ---
for k in "ABC":
    for nm in ("P08_PIV_%s"%k,"P08_SLV_%s"%k):
        o=bpy.data.objects[nm]
        rep[nm]={"loc":[round(v,4) for v in o.location],
                 "rot_deg":[round(math.degrees(v),3) for v in o.rotation_euler],
                 "rot_mode":o.rotation_mode,
                 "scale":[round(v,5) for v in o.scale],
                 "parent":o.parent.name if o.parent else None,
                 "mpi_is_identity":all(abs(o.matrix_parent_inverse[r][c]-(1.0 if r==c else 0.0))<1e-6 for r in range(4) for c in range(4)),
                 "world_loc":[round(v,3) for v in o.matrix_world.translation]}
# --- my SLVFX rig ---
col=bpy.data.collections.get("P08_SLVFX")
rep["SLVFX"]=[o.name for o in col.objects] if col else "MISSING"
print(json.dumps(rep,indent=1))
