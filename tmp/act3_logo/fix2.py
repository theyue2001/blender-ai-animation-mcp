import bpy
L=[]
img = bpy.data.images["NITE R1 LOGO-02.png"]
m = bpy.data.materials["MAT_P05_Logo"]
assert m.users == 1, "MAT_P05_Logo users=%d" % m.users
o = bpy.data.objects["X5_DECAL_NITE_R1_Logo"]
assert o.material_slots[0].link == 'OBJECT' and o.material_slots[0].material is m

nt = m.node_tree
if nt.animation_data: nt.animation_data_clear()
nt.nodes.clear()
out  = nt.nodes.new("ShaderNodeOutputMaterial");  out.name="Material Output";  out.location=(560,0)
mix  = nt.nodes.new("ShaderNodeMixShader");       mix.name="Mix Shader";       mix.location=(340,0)
tr   = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.name="Transparent BSDF";  tr.location=(120,140)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled");  bsdf.name="Principled BSDF"; bsdf.location=(60,-120)
tex  = nt.nodes.new("ShaderNodeTexImage");        tex.name="Image Texture";    tex.location=(-260,120)
tc   = nt.nodes.new("ShaderNodeTexCoord");        tc.name="Texture Coordinate";tc.location=(-460,120)
tex.image = img; tex.extension='CLIP'; tex.interpolation='Linear'
bsdf.inputs['Base Color'].default_value        = (0.80, 0.82, 0.86, 1.0)
bsdf.inputs['Metallic'].default_value          = 0.0
bsdf.inputs['Roughness'].default_value         = 0.34
bsdf.inputs['Specular IOR Level'].default_value= 0.35
nt.links.new(tc.outputs['UV'], tex.inputs['Vector'])
nt.links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
nt.links.new(tr.outputs['BSDF'], mix.inputs[1])
nt.links.new(bsdf.outputs['BSDF'], mix.inputs[2])
nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
L.append("rebuilt MAT_P05_Logo")
bpy.ops.wm.save_mainfile()
L.append("SAVED")
print("\n".join(L))
