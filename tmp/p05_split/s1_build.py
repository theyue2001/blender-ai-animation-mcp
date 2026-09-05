import bpy, json, math
from mathutils import Matrix

SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
log = []
prev_win = bpy.context.window.scene
bpy.context.window.scene = SC

GUARD = "_p05_worn_built"
root_exist = bpy.data.objects.get("P05_WORN_ROOT")
if root_exist and root_exist.get(GUARD):
    print(json.dumps({"skipped": "already built"})); raise SystemExit

# ---------- collections ----------
def getcoll(name, parent):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    if c.name not in [x.name for x in parent.children]:
        parent.children.link(c)
    return c

master = SC.collection
C_WORN  = getcoll("P05_WORN", master)
C_BODY  = getcoll("P05_WORN_BODY", C_WORN)
C_PROD  = getcoll("P05_WORN_PRODUCT", C_WORN)
C_LIGHT = getcoll("P05_WORN_LIGHT", C_WORN)

# ---------- root empty ----------
root = bpy.data.objects.get("P05_WORN_ROOT")
if root is None:
    root = bpy.data.objects.new("P05_WORN_ROOT", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.6
if root.name not in C_WORN.objects:
    C_WORN.objects.link(root)
root.matrix_basis = Matrix.Identity(4)

# ---------- material duplication ----------
SAFE = {"sin":math.sin,"cos":math.cos,"tan":math.tan,"pi":math.pi,"sqrt":math.sqrt,
        "abs":abs,"min":min,"max":max,"pow":pow,"exp":math.exp,"floor":math.floor,"ceil":math.ceil}

matmap = {}
def worn_mat(src):
    """copy a material, strip animation+drivers, freeze driven values at the 'off' state."""
    if src is None: return None
    if src.name in matmap: return matmap[src.name]
    new = src.copy()
    base = src.name
    for pre in ("MAT_P05_",):
        if base.startswith(pre): base = base[len(pre):]
    new.name = "MAT_P05W_" + base.replace("SHOT1_", "").replace(" ", "_").replace("#", "n")
    nt = new.node_tree
    frozen = []
    ad = nt.animation_data
    if ad:
        # freeze driver targets at variables = 0
        for dr in list(ad.drivers):
            try:
                val = eval(dr.driver.expression, {"__builtins__":{}}, dict(SAFE, **{v.name: 0.0 for v in dr.driver.variables}))
            except Exception as e:
                val = None
            frozen.append([dr.data_path, dr.array_index, val])
        # freeze action-driven values at frame 1700 (safe/settled state)
        if ad.action:
            for fc in ad.action.fcurves:
                frozen.append([fc.data_path, fc.array_index, float(fc.evaluate(1700))])
        nt.animation_data_clear()
    for dp, idx, val in frozen:
        if val is None: continue
        try:
            tgt = nt.path_resolve(dp.rsplit(".",1)[0] if False else dp, False)
            # dp resolves directly to the property (float or array)
            holder_path, prop = dp.rsplit(".",1)
            holder = nt.path_resolve(holder_path)
            cur = getattr(holder, prop)
            if hasattr(cur, "__len__") and not isinstance(cur, str):
                cur[idx] = val
            else:
                setattr(holder, prop, val)
        except Exception as e:
            frozen.append(["ERR "+dp, idx, str(e)]); break
    # human fade must be fully opaque
    if "SHOT1_HUMAN_Fade" in nt.nodes:
        nt.nodes["SHOT1_HUMAN_Fade"].inputs[0].default_value = 1.0
    matmap[src.name] = new
    log.append(["mat", src.name, new.name, frozen])
    return new

# ---------- object copies ----------
def world_of(o):
    if o.parent is None:
        return o.matrix_basis.copy()
    return world_of(o.parent) @ o.matrix_parent_inverse @ o.matrix_basis

made = []
def clone(src, newname, coll):
    c = src.copy()
    c.name = newname
    c.data = src.data          # linked mesh data (no duplication)
    c.animation_data_clear()
    c.parent = None
    c.hide_render = False
    c.hide_viewport = False
    c.matrix_basis = world_of(src)
    for sl in c.material_slots:
        pass
    # OBJECT-level material override
    for i, sl in enumerate(c.material_slots):
        srcmat = src.material_slots[i].material if i < len(src.material_slots) else None
        if srcmat is None:
            srcmat = c.data.materials[i] if i < len(c.data.materials) else None
        sl.link = 'OBJECT'
        sl.material = worn_mat(srcmat)
    coll.objects.link(c)
    c.parent = root
    c.matrix_parent_inverse = Matrix.Identity(4)
    made.append(c.name)
    return c

# product: all 43 X5_* from shell + internal
prod_src = []
for cn in ("P05_XRAY_SHELL", "P05_XRAY_INTERNAL"):
    prod_src += list(bpy.data.collections[cn].objects)
for o in prod_src:
    clone(o, "WRN_" + o.name.replace("X5_", ""), C_PROD)

# body + straps
for nm, new in (("Male","WRN_Male"), ("Underwear","WRN_Underwear"),
                ("P01_STRAP_UPPER","WRN_STRAP_UPPER"), ("P01_STRAP_LOWER","WRN_STRAP_LOWER")):
    clone(bpy.data.objects[nm], new, C_BODY)

root[GUARD] = 1
bpy.ops.wm.save_mainfile()

print(json.dumps({"objs": len(made), "mats": len(matmap),
                  "mat_names": sorted(m.name for m in matmap.values()),
                  "sample_log": log[:4],
                  "scene_objs": len(SC.objects)}, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev_win
