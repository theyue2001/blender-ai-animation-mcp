import bpy
sc=bpy.data.scenes["05_SCN_P07_STRAP_RIG"]
c=bpy.data.collections["P07_DEVICE_REF"]
o=bpy.data.objects.get("P07R_mesh.002")
if o:
    c.objects.unlink(o); bpy.data.objects.remove(o)
    print("removed heavy sleeve copy")
print("objs", len(sc.objects))
