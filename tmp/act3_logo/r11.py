import bpy
OUT = "D:/接案/26_0825_紅犀牛3D動畫/VScode/tmp/act3_logo"
L=[]
# --- integrity: which scenes use the new materials, and did X5 keep its own ---
new = [m for m in bpy.data.materials if m.name.startswith("MAT_P05W2_")]
bad=[]
for m in new:
    users=[o.name for o in bpy.data.objects for s in o.material_slots if s.material is m]
    if any(not u.startswith("WRN_") for u in users): bad.append((m.name,users))
L.append("new materials=%d  non-WRN users=%s" % (len(new), bad if bad else "none"))
x5=[o.name for o in bpy.data.objects if o.name.startswith("X5_") and o.type=='MESH'
    and (not o.material_slots or not o.material_slots[0].material)]
L.append("X5 objects missing material: %s" % (x5 if x5 else "none"))
orph=[m.name for m in bpy.data.materials if m.name.startswith("MAT_P05W_") and m.users==0]
L.append("orphaned old P05W materials: %s" % orph)
# scene 01 / 02 untouched?
for sn in ("01_SCN_OPENING_P01_P03","02_Scene_02_Page04_Material_Exterior_Quality"):
    sc=bpy.data.scenes[sn]
    leak=[o.name for o in sc.objects for s in o.material_slots if s.material and s.material.name.startswith("MAT_P05W")]
    L.append("%s objects on P05W materials: %s" % (sn, leak if leak else "none"))

def render(scname, frame, tag, bx=None, by=None, pct=100, samples=64):
    sc = bpy.data.scenes[scname]; prev = bpy.context.window.scene; pfr = sc.frame_current
    pe,pp = sc.render.engine, sc.render.resolution_percentage
    pb,pc,pf = sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath
    pss = sc.cycles.samples
    try:
        bpy.context.window.scene = sc; sc.frame_set(frame)
        sc.render.engine='CYCLES'; sc.render.resolution_percentage=pct
        crop = bx is not None
        sc.render.use_border=crop; sc.render.use_crop_to_border=crop
        if crop:
            sc.render.border_min_x,sc.render.border_max_x = bx
            sc.render.border_min_y,sc.render.border_max_y = by
        sc.cycles.samples=samples
        sc.render.filepath = OUT + "/" + tag + ".png"
        bpy.ops.render.render(write_still=True); return tag
    finally:
        sc.render.engine, sc.render.resolution_percentage = pe,pp
        sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath = pb,pc,pf
        sc.cycles.samples = pss; sc.frame_set(pfr); bpy.context.window.scene = prev
for f in (1340, 1349, 1378):
    L.append(render("03_SCN_P05_XRAY_MECHANISM", f, "press_%d"%f, (0.055,0.215),(0.28,0.56), samples=96))
print("\n".join(L))
