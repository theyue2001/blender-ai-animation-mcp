import bpy, json
out={}
for n in ["A","B","C"]:
    m=bpy.data.meshes.get(n) or bpy.data.meshes.get(n.upper())
for k in "ABC":
    o=bpy.data.objects["P08_CMP_%s"%k]
    out["CMP_"+k]={"mesh":o.data.name,"verts":len(o.data.vertices),"polys":len(o.data.polygons),
                   "mods":[m.type for m in o.modifiers]}
src={}
for nm in ["A","B","C"]:
    o=bpy.data.objects.get(nm)
    if o: src[nm]={"verts":len(o.data.vertices),"polys":len(o.data.polygons),"hide_render":o.hide_render,
                   "dims":[round(v,4) for v in o.dimensions],"scale":[round(v,4) for v in o.scale]}
out["src"]=src
out["cmp_lights"]=[(o.name,o.data.type,round(o.data.energy,1),[round(v,1) for v in o.location]) for o in bpy.data.collections["P08_FX"].objects if o.type=='LIGHT']
print(json.dumps(out,indent=1))
