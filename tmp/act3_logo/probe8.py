import bpy
L=[]
KEY=('Base Color','Metallic','Roughness','IOR','Alpha','Specular IOR Level','Coat Weight','Coat Roughness','Coat IOR','Transmission Weight','Sheen Weight','Emission Color','Emission Strength','Anisotropic')
def dump(mn, full=False):
    m=bpy.data.materials.get(mn)
    if not m: L.append("  %s : MISSING"%mn); return
    nt=m.node_tree
    L.append("=== %s (users=%d anim=%s) nodes=%d ===" % (m.name, m.users, bool(nt.animation_data and nt.animation_data.action), len(nt.nodes)))
    if nt.animation_data and nt.animation_data.action:
        for fc in nt.animation_data.action.fcurves:
            L.append("   FCU %s : %s" % (fc.data_path[:70], [(int(k.co[0]),round(k.co[1],3)) for k in fc.keyframe_points][:6]))
    out=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL']
    if out and out[0].inputs['Surface'].is_linked:
        L.append("   OUTPUT <- %s (%s)" % (out[0].inputs['Surface'].links[0].from_node.name, out[0].inputs['Surface'].links[0].from_node.type))
    L.append("   node types: %s" % sorted(set(n.type for n in nt.nodes)))
    for n in nt.nodes:
        if n.type=='BSDF_PRINCIPLED':
            vals=[]
            for k in KEY:
                if k in n.inputs:
                    i=n.inputs[k]
                    if i.is_linked: vals.append("%s<-%s"%(k,i.links[0].from_node.name))
                    else:
                        v=i.default_value
                        if hasattr(v,'__len__'): v=tuple(round(float(x),4) for x in v)
                        else: v=round(float(v),4)
                        vals.append("%s=%s"%(k,v))
            L.append("   [PRINCIPLED %s] %s" % (n.name, " ".join(vals)))
        elif n.type in ('MIX_SHADER','ADD_SHADER'):
            ins=[]
            for i in n.inputs:
                ins.append("%s<-%s"%(i.name,i.links[0].from_node.name) if i.is_linked else "%s=%s"%(i.name, round(i.default_value,3) if isinstance(i.default_value,float) else i.default_value))
            L.append("   [%s %s] %s" % (n.type, n.name, " | ".join(ins)))
        elif n.type=='BSDF_TRANSPARENT':
            c=n.inputs['Color']
            L.append("   [TRANSPARENT %s] Color=%s" % (n.name, "<-"+c.links[0].from_node.name if c.is_linked else tuple(round(float(x),4) for x in c.default_value)))
        elif n.type=='VALTORGB':
            L.append("   [RAMP %s] stops=%s" % (n.name, [(round(e.position,3), tuple(round(float(x),3) for x in e.color)) for e in n.color_ramp.elements]))
        elif n.type=='LAYER_WEIGHT':
            L.append("   [LAYERWEIGHT %s] Blend=%s" % (n.name, round(n.inputs['Blend'].default_value,3)))
        elif n.type=='VALUE':
            L.append("   [VALUE %s] = %.4f" % (n.name, n.outputs[0].default_value))
    L.append("")

for a,b in [("MAT_P05W_Shell_Smoked","Clear Rough Plastic Black #2"),
            ("MAT_P05W_Shell_Smoked_Rear","Paint Matte Black #2"),
            ("MAT_P05W_Shell_FrontPlate","Paint Matte Black #1.006"),
            ("MAT_P05W_Bezel_Steel","MAT_P04_Clean_Satin_Silver_Bezel")]:
    dump(a); dump(b)
dump("Paint Matte Black #1.007"); dump("Paint Matte Black #1.014"); dump("SHOT1_CONTROL_38_0.002_0")
print("\n".join(L))
