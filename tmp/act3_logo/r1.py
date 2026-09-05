import bpy, os
L=[]
sc = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
g = bpy.data.objects.get("P05_GOBO_RIGHT")
if g:
    L.append("GOBO %s: cam=%s diffuse=%s glossy=%s trans=%s shadow=%s volume=%s hide_r=%s mats=%s" % (
        g.name, g.visible_camera, g.visible_diffuse, g.visible_glossy, g.visible_transmission,
        g.visible_shadow, g.visible_volume_scatter, g.hide_render, [s.material.name if s.material else None for s in g.material_slots]))
    L.append("  loc(local)=%s scale=%s parent=%s" % (tuple(round(v,4) for v in g.location), tuple(round(v,3) for v in g.scale), g.parent.name if g.parent else None))

prev = bpy.context.window.scene
pe, pw, ph, pp = sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage
pb, pf = sc.render.use_border, sc.render.filepath
pss = sc.cycles.samples
try:
    bpy.context.window.scene = sc
    sc.frame_set(1396)
    sc.render.engine = 'CYCLES'
    sc.render.resolution_percentage = 100
    sc.render.use_border = True
    sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x = 0.04, 0.26
    sc.render.border_min_y, sc.render.border_max_y = 0.42, 0.78
    sc.cycles.samples = 64
    out = r"D:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\act3_logo\crop_1396.png"
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    L.append("rendered -> %s" % out)
finally:
    sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = pe, pw, ph, pp
    sc.render.use_border, sc.render.filepath = pb, pf
    sc.render.use_crop_to_border = False
    sc.cycles.samples = pss
    bpy.context.window.scene = prev
print("\n".join(L))
