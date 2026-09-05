import bpy
sc=bpy.data.scenes["05_SCN_P07_STRAP_RIG"]
objs=sorted([o for o in sc.objects if o.type=='MESH'], key=lambda o:-len(o.data.vertices))
tot=0
for o in objs[:12]:
    print(o.name, len(o.data.vertices))
tot=sum(len(o.data.vertices) for o in objs)
print("TOTAL verts", tot, "objects", len(objs))
