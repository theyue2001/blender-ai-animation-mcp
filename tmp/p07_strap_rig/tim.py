import bpy
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
out = []
fps = sc.render.fps / sc.render.fps_base
out.append("scene fps = %.3f (other scenes: %s)" %
           (fps, {s.name[:2]: round(s.render.fps / s.render.fps_base, 2) for s in bpy.data.scenes}))


def tc(t):
    return int(round(t * fps))


B = {"P07_1_08_ROTATE_IN": tc(68), "P07_1_16_TWIST_LOCK_STRAP_THREAD": tc(76),
     "P07_1_24_HANDS_FREE": tc(84), "P07_1_30_END": tc(90)}
sc.frame_start = B["P07_1_08_ROTATE_IN"]
sc.frame_end = B["P07_1_30_END"]
for m in list(sc.timeline_markers):
    sc.timeline_markers.remove(m)
sc.timeline_markers.new("P07_TESTPOSES_A_D", frame=1)
for k, v in B.items():
    sc.timeline_markers.new(k, frame=v)
out.append("frame range %d..%d ; markers %s" % (sc.frame_start, sc.frame_end,
                                                sorted((m.frame, m.name) for m in sc.timeline_markers)))

# isolate the device reference materials: past frame ~1174 the shared product
# materials hold IGNITION_Glow_Emission = 8.0 by constant extrapolation
made = {}
n_obj = 0
for o in sc.objects:
    if not o.name.startswith("P07R_") or o.type != 'MESH':
        continue
    touched = False
    for slot in o.material_slots:
        m = slot.material
        if m is None or m.name.startswith("MAT_P07"):
            continue
        key = m.name
        if key not in made:
            c = m.copy(); c.name = "MAT_P07R_" + key
            if c.animation_data:
                c.animation_data_clear()
            if c.use_nodes:
                nt = c.node_tree
                if nt.animation_data:
                    nt.animation_data_clear()
                outn = [x for x in nt.nodes if x.type == 'OUTPUT_MATERIAL']
                prn = [x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED']
                ign = [x for x in nt.nodes if "IGNITION" in x.name]
                if ign and outn and prn:
                    for l in list(outn[0].inputs['Surface'].links):
                        nt.links.remove(l)
                    nt.links.new(prn[0].outputs[0], outn[0].inputs['Surface'])
                for x in ign:
                    nt.nodes.remove(x)
            made[key] = c
        slot.link = 'OBJECT'
        slot.material = made[key]
        touched = True
    if touched:
        n_obj += 1
out.append("device refs isolated: %d objects, %d scene-local materials (OBJECT-linked)" % (n_obj, len(made)))

# sanity: originals untouched
bad = [o.name for o in bpy.data.objects
       if not o.name.startswith(("P07_", "P07R_")) and o.type == 'MESH'
       and any(s.link == 'OBJECT' and s.material and s.material.name.startswith("MAT_P07")
               for s in o.material_slots)]
out.append("objects outside P07 using P07 materials: %s" % (bad or "none"))
sc.frame_current = B["P07_1_16_TWIST_LOCK_STRAP_THREAD"]
print("\n".join(out))
