import bpy, json, math
from mathutils import Vector, Matrix, Euler
out={}
for k in "ABC":
    for pre in ("P08_CMP_","P08_SLV_"):
        o=bpy.data.objects[pre+k]
        M=Matrix.Translation(o.location) @ Euler(o.rotation_euler,'XYZ').to_matrix().to_4x4() @ Matrix.Diagonal(Vector((*o.scale,1.0)))
        bb=[M@Vector(c) for c in o.bound_box]
        mn=Vector((min(p[i] for p in bb) for i in range(3)))
        mx=Vector((max(p[i] for p in bb) for i in range(3)))
        lb=[Vector(c) for c in o.bound_box]
        lmn=Vector((min(p[i] for p in lb) for i in range(3))); lmx=Vector((max(p[i] for p in lb) for i in range(3)))
        lsz=lmx-lmn
        out[pre+k]={"world_size":[round(v,3) for v in (mx-mn)],
                    "world_centre":[round(v,3) for v in (mn+mx)/2],
                    "world_min":[round(v,2) for v in mn],"world_max":[round(v,2) for v in mx],
                    "local_size":[round(v,3) for v in lsz],
                    "local_long_axis":"XYZ"[max(range(3),key=lambda i:lsz[i])],
                    "scale":round(o.scale[0],5),
                    "rot_deg":[round(math.degrees(v),2) for v in o.rotation_euler],
                    "dimensions_prop":[round(v,3) for v in o.dimensions]}
cam=bpy.data.objects["CAM_P08_05_Compare"]
out["cam"]={"loc":[round(v,2) for v in cam.location],"rot":[round(math.degrees(v),2) for v in cam.rotation_euler],
            "lens":cam.data.lens,"clip":[cam.data.clip_start,cam.data.clip_end]}
print(json.dumps(out,indent=1))
