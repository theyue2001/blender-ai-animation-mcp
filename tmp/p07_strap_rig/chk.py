import bpy
for nm in ("64.002","65.002","59.002","60.002"):
    o=bpy.data.objects[nm]
    print("%-9s colls=%s users=%d scenes=%s"%(nm,[c.name for c in o.users_collection],o.users,[s.name for s in o.users_scene]))
for c in bpy.data.collections:
    if any(o.name in ("64.002","65.002") for o in c.objects):
        print("collection %-28s in scenes=%s children_of=%s"%(c.name,[s.name for s in bpy.data.scenes if c in list(s.collection.children_recursive)+[s.collection]],[p.name for p in bpy.data.collections if c in list(p.children)]))
