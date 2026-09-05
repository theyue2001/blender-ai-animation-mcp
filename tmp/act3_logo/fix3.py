import bpy
L=[]

# WRN object -> scene-01 source object whose material is the reference
SRC = {}
for o in bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"].objects:
    if o.name.startswith("WRN_"):
        SRC[o.name] = o.name[4:]
SRC["WRN_STRAP_UPPER"] = "P01_STRAP_UPPER"
SRC["WRN_STRAP_LOWER"] = "P01_STRAP_LOWER"

# keep P05-specific animated / deliberately tuned looks
SKIP = {"WRN_Male","WRN_Underwear",                    # P05-tuned skin + briefs
        "WRN_49.002",                                   # control plate: button press rig
        "WRN_Disc.002","WRN_Disc #1.002","WRN_Disc #2.002",  # LED step animation
        "WRN_DECAL_NITE_R1_Logo"}                       # already matched to scene 01

cache = {}
def make_copy(srcmat):
    if srcmat.name in cache: return cache[srcmat.name]
    m = srcmat.copy()
    m.name = "MAT_P05W2_" + srcmat.name.replace(" ","_").replace("#","n")
    nt = m.node_tree
    if nt.animation_data: nt.animation_data_clear()
    out = next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
    if out.inputs['Surface'].is_linked:
        head = out.inputs['Surface'].links[0].from_node
        # step past the ignition add-shader to the real surface
        if head.name.startswith("IGNITION") and head.type=='ADD_SHADER' and head.inputs[0].is_linked:
            surf_sock = head.inputs[0].links[0].from_socket
            nt.links.new(surf_sock, out.inputs['Surface'])
    for n in [n for n in nt.nodes if n.name.startswith("IGNITION")]:
        nt.nodes.remove(n)
    # any *_Fade mix shader: force fully-visible
    for n in nt.nodes:
        if n.type=='MIX_SHADER' and n.name.endswith("_Fade") and not n.inputs[0].is_linked:
            n.inputs[0].default_value = 1.0
    cache[srcmat.name] = m
    return m

done=[]; skipped=[]; noref=[]
for wn, sn in sorted(SRC.items()):
    if wn in SKIP: skipped.append(wn); continue
    wo = bpy.data.objects[wn]; so = bpy.data.objects.get(sn)
    if not so or not so.material_slots or not so.material_slots[0].material:
        noref.append((wn,sn)); continue
    old = wo.material_slots[0].material.name
    new = make_copy(so.material_slots[0].material)
    wo.material_slots[0].link = 'OBJECT'
    wo.material_slots[0].material = new
    done.append("  %-30s %-30s -> %s  (src %s)" % (wn, old, new.name, so.material_slots[0].material.name))

L.append("CONVERTED %d objects, %d new materials" % (len(done), len(cache)))
L += done
L.append("SKIPPED (kept P05 look): %s" % sorted(skipped))
L.append("NO REFERENCE: %s" % noref)
bpy.ops.wm.save_mainfile()
L.append("SAVED")
print("\n".join(L))
