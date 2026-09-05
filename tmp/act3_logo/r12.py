import bpy
OUT = "D:/接案/26_0825_紅犀牛3D動畫/VScode/tmp/act3_logo"
def render(scname, frame, tag, bx, by, samples=96):
    sc = bpy.data.scenes[scname]; prev = bpy.context.window.scene; pfr = sc.frame_current
    pe,pp = sc.render.engine, sc.render.resolution_percentage
    pb,pc,pf = sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath
    pss = sc.cycles.samples
    try:
        bpy.context.window.scene = sc; sc.frame_set(frame)
        sc.render.engine='CYCLES'; sc.render.resolution_percentage=100
        sc.render.use_border=True; sc.render.use_crop_to_border=True
        sc.render.border_min_x,sc.render.border_max_x = bx
        sc.render.border_min_y,sc.render.border_max_y = by
        sc.cycles.samples=samples
        sc.render.filepath = OUT + "/" + tag + ".png"
        bpy.ops.render.render(write_still=True); return tag
    finally:
        sc.render.engine, sc.render.resolution_percentage = pe,pp
        sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath = pb,pc,pf
        sc.cycles.samples = pss; sc.frame_set(pfr); bpy.context.window.scene = prev

m = bpy.data.materials["MAT_P05W_Control_Plate"]
b = next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
keep = {k: (tuple(b.inputs[k].default_value) if hasattr(b.inputs[k].default_value,'__len__') else b.inputs[k].default_value)
        for k in ('Base Color','Metallic','Roughness','Specular IOR Level','Coat Weight')}
try:
    b.inputs['Base Color'].default_value=(0.03,0.032,0.038,1.0)
    b.inputs['Metallic'].default_value=0.2
    b.inputs['Roughness'].default_value=0.28
    b.inputs['Specular IOR Level'].default_value=0.5
    b.inputs['Coat Weight'].default_value=0.1
    for f in (1340,1349,1378):
        render("03_SCN_P05_XRAY_MECHANISM", f, "oldbase_%d"%f, (0.055,0.215),(0.28,0.56))
finally:
    for k,v in keep.items(): b.inputs[k].default_value = v
print("done; base restored to", tuple(round(float(x),4) for x in b.inputs['Base Color'].default_value), b.inputs['Metallic'].default_value, b.inputs['Roughness'].default_value)
