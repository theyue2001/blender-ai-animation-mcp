import bpy
L=[]
sc = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
L.append("=== SCENE 03 COLLECTIONS ===")
def walk(c, d=0):
    L.append("  "*d + "[%s] objs=%d" % (c.name, len(c.objects)))
    for ch in c.children: walk(ch, d+1)
walk(sc.collection)
L.append("=== SCENE 03 OBJECTS (name / type / parent) ===")
for o in sorted(sc.objects, key=lambda x: x.name):
    L.append("  %-42s %-10s parent=%s" % (o.name, o.type, o.parent.name if o.parent else "-"))
L.append("")
L.append("=== ALL LOGO-ISH OBJECTS IN FILE ===")
for o in bpy.data.objects:
    n=o.name.upper()
    if "LOGO" in n or "DECAL" in n or "EMBOSS" in n:
        scs = [s.name for s in bpy.data.scenes if o.name in s.objects]
        L.append("  %-46s mesh=%-34s hide_v=%s hide_r=%s parent=%-16s scenes=%s" % (
            o.name, (o.data.name if o.type=='MESH' else '-'), o.hide_viewport, o.hide_render,
            o.parent.name if o.parent else "-", scs))
print("\n".join(L))
