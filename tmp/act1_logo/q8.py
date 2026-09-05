import bpy, json, math
from mathutils import Vector, Matrix
sc=[s for s in bpy.data.scenes if "CAM_Opening_Silhouette" in s.objects][0]
F=426
out={}
# ---- exclusivity of the SHOT1_CONTROL_* materials ----
inst_colls = {}
for o in bpy.data.objects:
    if o.instance_collection: inst_colls.setdefault(o.instance_collection.name,[]).append(o.name)
out["who_instances"]={k:v for k,v in inst_colls.items() if "OPENING" in k or "P04" in k}
mats={}
for m in bpy.data.materials:
    if m.name.startswith("SHOT1_CONTROL"):
        users=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)]
        colls=sorted({c.name for n in users for c in bpy.data.objects[n].users_collection})
        p=m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
        mats[m.name]={"users":m.users,"objs":users,"colls":colls,
                      "base":[round(v,4) for v in p.inputs["Base Color"].default_value] if p else None,
                      "rough":round(p.inputs["Roughness"].default_value,3) if p else None,
                      "metal":round(p.inputs["Metallic"].default_value,3) if p else None,
                      "spec":round(p.inputs["Specular IOR Level"].default_value,3) if p and "Specular IOR Level" in p.inputs else None,
                      "coat":round(p.inputs["Coat Weight"].default_value,3) if p and "Coat Weight" in p.inputs else None,
                      "basecol_linked": bool(p.inputs["Base Color"].links) if p else None}
out["shot1_control_mats"]=mats
# ---- camera at F, analytic ----
cam=sc.objects["CAM_Opening_Silhouette"]
loc=Vector([f.evaluate(F) for f in sorted([fc for fc in cam.animation_data.action.fcurves if fc.data_path=="location"], key=lambda x:x.array_index)])
tgt=bpy.data.objects["CTRL_Opening_Silhouette_Target"].matrix_basis.translation
q=(tgt-loc).to_track_quat('-Z','Y')
Mcam=Matrix.Translation(loc) @ q.to_matrix().to_4x4()
Minv=Mcam.inverted()
lens=cam.data.lens; sw=cam.data.sensor_width; W,H=1920,1080
tx=(sw/2)/lens; ty=tx*H/W
def proj(p):
    v=Minv @ p
    if v.z>=-1e-6: return None
    return ((v.x/-v.z)/tx*0.5+0.5)*W, (1-((v.y/-v.z)/ty*0.5+0.5))*H
out["cam"]={"loc":[round(v,3) for v in loc],"px_logo":None}
lg=bpy.data.objects["P01_DECAL_NITE_R1_Logo_Reveal"]
M=lg.matrix_basis
vs=[M @ v.co for v in lg.data.vertices]
c=sum(vs,Vector((0,0,0)))/len(vs)
pj=proj(c)
out["cam"]["px_logo"]=[round(x) for x in pj] if pj else None
# ---- project bboxes of front objects ----
def wm(o):
    m=o.matrix_basis.copy(); cur=o
    while cur.parent is not None:
        m=cur.parent.matrix_basis @ cur.matrix_parent_inverse @ m; cur=cur.parent
    return m
srcc=bpy.data.collections["SRC_OPENING_NITE_PRODUCT_LINKED"]
proj_out=[]
for o in srcc.all_objects:
    if o.type!='MESH' or not len(o.data.vertices): continue
    M=wm(o); pts=[proj(M @ Vector(v)) for v in o.bound_box]
    pts=[p for p in pts if p]
    if len(pts)<8: continue
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    if max(xs)<600 or min(xs)>1350 or max(ys)<600 or min(ys)>1080: continue
    proj_out.append({"n":o.name,"px":[round(min(xs)),round(min(ys)),round(max(xs)),round(max(ys))],
                     "mat":o.material_slots[0].material.name if o.material_slots and o.material_slots[0].material else None,
                     "sc01_only": len(o.users_collection)==1})
out["front_lower_objs"]=sorted(proj_out,key=lambda r:(r["px"][2]-r["px"][0])*(r["px"][3]-r["px"][1]))
print(json.dumps(out, ensure_ascii=False, indent=1))
