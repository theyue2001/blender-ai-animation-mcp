import bpy, json
from mathutils import Vector
o = bpy.data.objects["WRN_49.002"]; me = o.data
vs = [v.co.copy() for v in me.vertices]
lo = min(v.z for v in vs); hi = max(v.z for v in vs)
out = {"lo":round(lo,3), "hi":round(hi,3)}
for side, band in (("lo", 2.4), ("hi", 2.4)):
    ref = lo if side=="lo" else hi
    sel = [v for v in vs if (v.z < ref+band if side=="lo" else v.z > ref-band)]
    cl=[]
    for v in sel:
        for c in cl:
            if (v.x-c["x"])**2+(v.y-c["y"])**2 < 5.5**2:
                c["n"]+=1; c["sx"]+=v.x; c["sy"]+=v.y; c["sz"]+=v.z
                c["x"]=c["sx"]/c["n"]; c["y"]=c["sy"]/c["n"]; break
        else:
            cl.append({"x":v.x,"y":v.y,"n":1,"sx":v.x,"sy":v.y,"sz":v.z})
    cl=[c for c in cl if c["n"]>=15]; cl.sort(key=lambda c:-c["n"])
    out[side+"_n"]=len(sel)
    out[side+"_clusters"]=[{"x":round(c["x"],2),"y":round(c["y"],2),"z":round(c["sz"]/c["n"],2),"n":c["n"]} for c in cl[:12]]
# world position of each cluster centre for the lo side
M = o.matrix_basis
out["scale"] = round(M.to_scale()[0], 5)
print(json.dumps(out, ensure_ascii=False, indent=1))
