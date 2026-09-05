import bpy, json
sc = [s for s in bpy.data.scenes if "CAM_Opening_Silhouette" in s.objects][0]
coll = bpy.data.collections["OPENING_P01_P03"]
src = bpy.data.objects["P04_DECAL_NITE_R1_Logo_Reveal"]
NAME = "P01_DECAL_NITE_R1_Logo_Reveal"
MATN = "MAT_P01_FRONT_LOGO_REVEAL"
log = {}

old = bpy.data.objects.get(NAME)
if old:
    for c in list(old.users_collection): c.objects.unlink(old)
    bpy.data.objects.remove(old)
    log["removed_old_obj"]=True
om = bpy.data.materials.get(MATN)
if om:
    bpy.data.materials.remove(om); log["removed_old_mat"]=True

o = src.copy()              # shares mesh data -> ~0 MB
o.name = NAME
o.animation_data_clear()    # drop P04 visibility keys
coll.objects.link(o)
o.hide_render = False
o.hide_viewport = False

m = bpy.data.materials["MAT_P04_FRONT_LOGO_REVEAL"].copy()
m.name = MATN
if m.node_tree: m.node_tree.animation_data_clear()
o.material_slots[0].link = 'OBJECT'
o.material_slots[0].material = m
p = m.node_tree.nodes["Principled BSDF"]
ign = m.node_tree.nodes.get("IGNITION_Glow_Emission")
if ign: ign.inputs[1].default_value = 0.0
p.inputs["Roughness"].default_value = 0.40
p.inputs["Metallic"].default_value = 0.0
p.inputs["Emission Strength"].default_value = 0.0
p.inputs["Base Color"].default_value = (0.60, 0.62, 0.66, 1.0)   # probe value

log["obj"] = o.name
log["colls"] = [c.name for c in o.users_collection]
log["mat"] = (o.material_slots[0].link, o.material_slots[0].material.name, m.users)
log["mesh"] = (o.data.name, o.data.users)
log["in_scenes"] = [s.name for s in bpy.data.scenes if o.name in s.objects]
log["links"] = [(l.from_node.name, l.from_socket.name, "->", l.to_node.name, l.to_socket.name) for l in m.node_tree.links]
log["fade_fac"] = m.node_tree.nodes["SHOT1_NITE_LOGO_Fade"].inputs[0].default_value
bpy.ops.wm.save_mainfile()
log["saved"] = True
print(json.dumps(log, ensure_ascii=False, indent=1))
