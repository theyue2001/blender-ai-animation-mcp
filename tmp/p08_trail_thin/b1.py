import bpy, json, math
from mathutils import Vector
SC=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
rep={}

# ---- reference: shot-1 dot constraint settings ----
ref=bpy.data.objects["P08_FXDOT_BLUE"].constraints["Follow Path"]
REFC={"use_curve_follow":ref.use_curve_follow,"use_fixed_location":ref.use_fixed_location,
      "forward_axis":ref.forward_axis,"up_axis":ref.up_axis,"use_curve_radius":ref.use_curve_radius}
rep["ref_constraint"]=REFC
rep["taper_users"]=bpy.data.objects["P08_TRAIL_TAPER"].users

# ---- who uses the sleeve materials / TUN visibility ----
rep["mat_users"]={}
for k in "ABC":
    m=bpy.data.materials["MAT_P08_SLEEVE_%s"%k]
    rep["mat_users"][k]=[o.name for o in bpy.data.objects if any(s.material==m for s in o.material_slots)]
# scene-level anim (fade at cut?)
ad=SC.animation_data
rep["scene_keys"]=sorted(set(f.data_path for f in ad.action.fcurves)) if (ad and ad.action) else None

# ---- world bbox centre of each sleeve ----
cent={}
for k in "ABC":
    o=bpy.data.objects["P08_SLV_%s"%k]
    mw=o.matrix_world
    bb=[mw@Vector(c) for c in o.bound_box]
    c=sum(bb,Vector())/8.0
    cent[k]=c
    rep.setdefault("centres",{})[k]=[round(v,3) for v in c]
    rep.setdefault("base_scale",{})[k]=[round(v,5) for v in o.scale]
print(json.dumps(rep,indent=1))
