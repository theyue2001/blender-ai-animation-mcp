import bpy
L=[]

logo_obj = bpy.data.objects["WRN_DECAL_NITE_R1_Logo"]
me = logo_obj.data
L.append("mesh=%s uv_layers=%s users=%d" % (me.name, [l.name for l in me.uv_layers], me.users))

img = bpy.data.images.get("NITE R1 LOGO-02.png")
L.append("image=%s size=%s alpha=%s" % (img.name if img else None, tuple(img.size) if img else None, img.alpha_mode if img else None))
assert img is not None

src = bpy.data.materials["MAT_P01_FRONT_LOGO_REVEAL"]
m = bpy.data.materials["MAT_P05W_Logo"]
assert m.users == 1, "MAT_P05W_Logo has %d users - unsafe to edit" % m.users

nt = m.node_tree
if nt.animation_data: nt.animation_data_clear()
nt.nodes.clear()

out  = nt.nodes.new("ShaderNodeOutputMaterial");  out.name="Material Output";  out.location=(560,0)
mix  = nt.nodes.new("ShaderNodeMixShader");       mix.name="Mix Shader";       mix.location=(340,0)
tr   = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.name="Transparent BSDF";  tr.location=(120,140)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled");  bsdf.name="Principled BSDF"; bsdf.location=(60,-120)
tex  = nt.nodes.new("ShaderNodeTexImage");        tex.name="Image Texture";    tex.location=(-260,120)
tc   = nt.nodes.new("ShaderNodeTexCoord");        tc.name="Texture Coordinate";tc.location=(-460,120)

tex.image = img
tex.extension = 'CLIP'
tex.interpolation = 'Linear'

# match the scene-01 / P04 reveal look, neutral-light so it reads white on the black dome
bsdf.inputs['Base Color'].default_value        = (0.80, 0.82, 0.86, 1.0)
bsdf.inputs['Metallic'].default_value          = 0.0
bsdf.inputs['Roughness'].default_value         = 0.34
bsdf.inputs['Specular IOR Level'].default_value= 0.35
bsdf.inputs['Emission Strength'].default_value = 0.0

nt.links.new(tc.outputs['UV'],   tex.inputs['Vector'])
nt.links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
nt.links.new(tr.outputs['BSDF'],   mix.inputs[1])
nt.links.new(bsdf.outputs['BSDF'], mix.inputs[2])
nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])

m.blend_method = 'HASHED' if hasattr(m,'blend_method') else m.blend_method
L.append("rebuilt %s: nodes=%s" % (m.name, [n.name for n in nt.nodes]))
L.append("slot link on object: %s -> %s" % (logo_obj.material_slots[0].link, logo_obj.material_slots[0].material.name))

bpy.ops.wm.save_mainfile()
L.append("SAVED %s" % bpy.data.filepath)
print("\n".join(L))
