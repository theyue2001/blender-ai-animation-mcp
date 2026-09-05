import bpy, json
from mathutils import Matrix, Vector
sc = bpy.data.scenes["01_SCN_OPENING_P01_P03"]
out={}
out["cycles"]={"samples":sc.cycles.samples,"prev":sc.cycles.preview_samples,"denoise":sc.cycles.use_denoising,
               "max_bounces":sc.cycles.max_bounces,"film_transparent":sc.render.film_transparent}
# world matrix analytically
def wm(o):
    m = o.matrix_basis.copy()
    p = o.parent
    while p is not None:
        m = p.matrix_basis @ o.matrix_parent_inverse @ m if False else m
        break
    # proper: walk chain
    m = o.matrix_basis.copy()
    cur = o
    while cur.parent is not None:
        m = cur.parent.matrix_basis @ cur.matrix_parent_inverse @ m
        cur = cur.parent
    return m
names = ["DECAL_NITE_R1_Logo","16_0.002","58.002","P04_DECAL_NITE_R1_Logo_Reveal"]
for n in names:
    o = bpy.data.objects.get(n)
    if not o: out[n]="MISSING"; continue
    m = wm(o)
    out[n]={"loc":[round(v,4) for v in m.translation],
            "parent":o.parent.name if o.parent else None,
            "colls":[c.name for c in o.users_collection],
            "hide_r":o.hide_render,"hide_v":o.hide_viewport,
            "mats":[(s.name if s.material else None, s.link) for s in o.material_slots],
            "verts": len(o.data.vertices) if o.type=='MESH' else None,
            "mesh": o.data.name if o.type=='MESH' else None,
            "in_sc01": o.name in sc.objects,
            "act": o.animation_data.action.name if o.animation_data and o.animation_data.action else None}
# which collections does SRC_OPENING_NITE_PRODUCT_LINKED contain
src = bpy.data.collections.get("SRC_OPENING_NITE_PRODUCT_LINKED")
if src:
    out["src_children"]=[c.name for c in src.children]
    out["src_has_decal"]= "DECAL_NITE_R1_Logo" in src.all_objects
    out["src_nobj"]=len(src.all_objects)
print(json.dumps(out, ensure_ascii=False, indent=1))
