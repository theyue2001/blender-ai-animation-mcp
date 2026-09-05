import bpy, json, math
from mathutils import Vector, Matrix
log={}
sc = [s for s in bpy.data.scenes if "CAM_Opening_Silhouette" in s.objects][0]
coll = bpy.data.collections["OPENING_P01_P03"]
o = bpy.data.objects["P01_DECAL_NITE_R1_Logo_Reveal"]
M = o.matrix_basis
vs = [M @ v.co for v in o.data.vertices]
ctr = sum(vs, Vector((0,0,0))) / len(vs)
mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
# plane normal from mesh polygons (local -> world, ignore translation)
R = M.to_3x3()
nrm = Vector((0,0,0))
for p in o.data.polygons: nrm += (R @ p.normal)
nrm.normalize()
if nrm.y < 0: nrm = -nrm      # must face +Y toward the camera
log["logo_center"]=[round(v,4) for v in ctr]
log["logo_bbox"]=[[round(v,4) for v in mn],[round(v,4) for v in mx]]
log["logo_size"]=[round(mx[i]-mn[i],4) for i in range(3)]
log["normal"]=[round(v,4) for v in nrm]

# ---- warm-neutral base colour to counter the blue key ----
m = bpy.data.materials["MAT_P01_FRONT_LOGO_REVEAL"]
p = m.node_tree.nodes["Principled BSDF"]
p.inputs["Base Color"].default_value = (0.76, 0.72, 0.66, 1.0)

# ---- light-linked logo highlight ----
LN="LGT_Opening_Logo_Highlight"; LL="LL_P01_Logo_Highlight"
old = bpy.data.objects.get(LN)
if old:
    d=old.data
    for c in list(old.users_collection): c.objects.unlink(old)
    bpy.data.objects.remove(old); bpy.data.lights.remove(d)
llc = bpy.data.collections.get(LL)
if llc is None:
    llc = bpy.data.collections.new(LL)
for ob in list(llc.objects): llc.objects.unlink(ob)
llc.objects.link(o)

ld = bpy.data.lights.new(LN, type='AREA')
ld.shape='DISK'; ld.size=0.30; ld.energy=6.0; ld.color=(1.0,0.95,0.88)
lo = bpy.data.objects.new(LN, ld)
DIST = 0.9
lo.location = ctr + nrm*DIST
lo.rotation_euler = (-nrm).to_track_quat('-Z','Y').to_euler()
coll.objects.link(lo)
try:
    lo.light_linking.receiver_collection = llc
    log["light_linking"]="ok"
except Exception as e:
    log["light_linking"]="FAILED: %r"%(e,)
log["light_loc"]=[round(v,4) for v in lo.location]
log["light_rot"]=[round(v,4) for v in lo.rotation_euler]
bpy.ops.wm.save_mainfile()
log["saved"]=True
print(json.dumps(log, ensure_ascii=False, indent=1))
