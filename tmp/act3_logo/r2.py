import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
L=[]
OUT = r"D:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\act3_logo"

def render_crop(scname, frame, bx, by, tag, samples=48):
    sc = bpy.data.scenes[scname]
    prev = bpy.context.window.scene
    pe, pp = sc.render.engine, sc.render.resolution_percentage
    pb, pc, pf = sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath
    pss = sc.cycles.samples
    pmk = [(m, m.camera) for m in sc.timeline_markers]
    try:
        bpy.context.window.scene = sc
        sc.frame_set(frame)
        sc.render.engine='CYCLES'; sc.render.resolution_percentage=100
        sc.render.use_border=True; sc.render.use_crop_to_border=True
        sc.render.border_min_x,sc.render.border_max_x = bx
        sc.render.border_min_y,sc.render.border_max_y = by
        sc.cycles.samples=samples
        p = OUT + "\\" + tag + ".png"
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        return p
    finally:
        sc.render.engine, sc.render.resolution_percentage = pe, pp
        sc.render.use_border, sc.render.use_crop_to_border, sc.render.filepath = pb, pc, pf
        sc.cycles.samples = pss
        for m,c in pmk: m.camera = c
        bpy.context.window.scene = prev

# --- 1) emissive tag test on the WRN logo ---
m = bpy.data.materials["MAT_P05W_Logo"]
bsdf = [n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
old_ec = tuple(bsdf.inputs['Emission Color'].default_value)
old_es = bsdf.inputs['Emission Strength'].default_value
try:
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.0, 0.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 30.0
    p1 = render_crop("03_SCN_P05_XRAY_MECHANISM", 1396, (0.04,0.26), (0.42,0.78), "tag_1396")
    L.append("tag render -> " + p1)
finally:
    bsdf.inputs['Emission Color'].default_value = old_ec
    bsdf.inputs['Emission Strength'].default_value = old_es

# --- 2) scene 01 reference: where is the logo on screen ---
sc1 = bpy.data.scenes["01_SCN_OPENING_P01_P03"]
prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc1
    sc1.frame_set(340)
    dg = bpy.context.evaluated_depsgraph_get()
    cam1 = sc1.camera
    mk = [m for m in sc1.timeline_markers if m.camera]
    L.append("scene01 scene.camera=%s markers=%s" % (cam1.name, [(m.frame,m.name,m.camera.name) for m in mk]))
    lo = bpy.data.objects["P01_DECAL_NITE_R1_Logo_Reveal"]
    le = lo.evaluated_get(dg); me = le.to_mesh()
    ws = [le.matrix_world @ v.co for v in me.vertices]; le.to_mesh_clear()
    ctr = sum(ws, Vector())/len(ws)
    RX,RY = sc1.render.resolution_x, sc1.render.resolution_y
    def proj(sc,cam,p):
        c = world_to_camera_view(sc,cam,p); return (c.x, 1-c.y)
    xs=[proj(sc1,cam1,v)[0] for v in ws]; ys=[proj(sc1,cam1,v)[1] for v in ws]
    L.append("scene01 res=%dx%d logo ndc x=%.4f..%.4f y=%.4f..%.4f  px=(%d..%d, %d..%d)" % (
        RX,RY,min(xs),max(xs),min(ys),max(ys), min(xs)*RX,max(xs)*RX,min(ys)*RY,max(ys)*RY))
    # fade node value at 340
    mm = bpy.data.materials["MAT_P01_FRONT_LOGO_REVEAL"]
    for n in mm.node_tree.nodes:
        if n.name in ("SHOT1_NITE_LOGO_Fade",):
            L.append("  Fade node inputs: " + str([(i.name, getattr(i,'default_value',None)) for i in n.inputs if not i.is_linked]))
    L.append("  LGT_Opening_Logo_Highlight energy=%s" % bpy.data.objects["LGT_Opening_Logo_Highlight"].data.energy)
finally:
    bpy.context.window.scene = prev
print("\n".join(L))
