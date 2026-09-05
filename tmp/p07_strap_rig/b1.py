import bpy
from mathutils import Vector, Matrix
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p:
        m=p.matrix_basis @ c.matrix_parent_inverse @ m; c=p; p=p.parent
    return m
SN="05_SCN_P07_STRAP_RIG"
if SN in bpy.data.scenes:
    print("scene exists"); raise SystemExit
sc = bpy.data.scenes.new(SN)
sc.frame_start=1; sc.frame_end=240; sc.frame_current=1
sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=800; sc.render.resolution_y=800; sc.render.resolution_percentage=100
sc.render.film_transparent=False
# world
w = bpy.data.worlds.new("W_P07")
w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.05,0.05,0.055,1)
w.node_tree.nodes["Background"].inputs[1].default_value=1.0
sc.world=w
root = bpy.data.collections.new("P07_STRAP_RIG")
sc.collection.children.link(root)
c_dev = bpy.data.collections.new("P07_DEVICE_REF"); root.children.link(c_dev)
c_body= bpy.data.collections.new("P07_BODY_REF");  root.children.link(c_body)
c_rig = bpy.data.collections.new("P07_RIG");       root.children.link(c_rig)
c_util= bpy.data.collections.new("P07_UTIL");      root.children.link(c_util)

src = bpy.data.collections["SRC_P04_NITE_PRODUCT_CLEAN_BEZEL"]
n=0
for o in src.objects:
    if o.type!='MESH': continue
    c = o.copy(); c.name = "P07R_"+o.name
    c.parent=None; c.matrix_world = wmat(o)
    c.hide_render=False; c.hide_viewport=False
    c_dev.objects.link(c); n+=1
for nm in ("Male","Underwear"):
    o=bpy.data.objects[nm]
    c=o.copy(); c.name="P07R_"+nm; c.parent=None; c.matrix_world=wmat(o)
    c.hide_render=False
    c_body.objects.link(c)
# light
lt = bpy.data.lights.new("P07_KEY", 'AREA'); lt.energy=2000; lt.size=4
lo = bpy.data.objects.new("P07_KEY", lt); lo.location=(3,-6,4)
lo.rotation_euler=(0.9,0,0.5)
c_util.objects.link(lo)
lt2 = bpy.data.lights.new("P07_FILL", 'AREA'); lt2.energy=800; lt2.size=6
lo2 = bpy.data.objects.new("P07_FILL", lt2); lo2.location=(-4,-5,2); lo2.rotation_euler=(1.3,0,-0.8)
c_util.objects.link(lo2)
cam = bpy.data.cameras.new("P07_QA_CAM"); cam.lens=60
co = bpy.data.objects.new("P07_QA_CAM", cam); c_util.objects.link(co)
sc.camera = co
print("created scene %s, device copies=%d, objs=%d" % (SN, n, len(sc.objects)))
