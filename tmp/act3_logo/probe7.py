import bpy
L=[]
sc3 = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
# WRN_x -> source object name
def src_name(n):
    return n[4:]  # strip "WRN_"
L.append("%-30s %-34s | %-30s %s" % ("WRN OBJ","WRN MAT (link)","SRC OBJ","SRC MAT (link)"))
L.append("-"*130)
missing=[]
for o in sorted(sc3.objects, key=lambda x:x.name):
    if not o.name.startswith("WRN_"): continue
    wm = [(s.material.name if s.material else None, s.link) for s in o.material_slots]
    sn = src_name(o.name)
    so = bpy.data.objects.get(sn)
    # map the renamed strap/body copies
    if so is None:
        alt = {"STRAP_UPPER":"P01_STRAP_UPPER","STRAP_LOWER":"P01_STRAP_LOWER"}.get(sn)
        if alt: so = bpy.data.objects.get(alt); sn = alt
    sm = [(s.material.name if s.material else None, s.link) for s in so.material_slots] if so else None
    L.append("%-30s %-34s | %-30s %s" % (o.name, str(wm)[:34], sn if so else "??", str(sm)[:60]))
print("\n".join(L))
