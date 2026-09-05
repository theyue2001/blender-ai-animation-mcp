import bpy
L=[]
def dump(mn):
    m=bpy.data.materials.get(mn)
    if not m: L.append("%s MISSING"%mn); return
    nt=m.node_tree
    L.append("=== %s (users=%d, blend=%s, animdata=%s) ===" % (m.name, m.users, m.blend_method if hasattr(m,'blend_method') else '-', bool(nt.animation_data and nt.animation_data.action)))
    if nt.animation_data and nt.animation_data.action:
        for fc in nt.animation_data.action.fcurves:
            L.append("   FCU %s : %s" % (fc.data_path, [(int(k.co[0]),round(k.co[1],3)) for k in fc.keyframe_points][:8]))
    for n in nt.nodes:
        extra=""
        if n.type=='TEX_IMAGE':
            im=n.image
            extra=" image=%s src=%s file=%s size=%s alpha_mode=%s colorspace=%s ext=%s" % (
                im.name if im else None, im.source if im else None, (im.filepath if im else None), tuple(im.size) if im else None,
                im.alpha_mode if im else None, im.colorspace_settings.name if im else None, n.extension)
        if n.type=='VALUE': extra=" value=%.4f" % n.outputs[0].default_value
        ins=[]
        for i in n.inputs:
            if i.is_linked:
                ln=i.links[0]
                ins.append("%s<-%s.%s" % (i.name, ln.from_node.name, ln.from_socket.name))
            else:
                v=getattr(i,'default_value',None)
                if hasattr(v,'__len__') and not isinstance(v,str): v=tuple(round(float(x),4) for x in v)
                elif isinstance(v,float): v=round(v,4)
                ins.append("%s=%s" % (i.name, v))
        L.append("  [%s] %s%s" % (n.type, n.name, extra))
        L.append("      " + " | ".join(ins))
    L.append("")

dump("SHOT1_NITE_LOGO_DECAL_NITE_R1_Logo_0")
dump("MAT_P01_FRONT_LOGO_REVEAL")
dump("MAT_P05W_Logo")
dump("MAT_P05_Logo")
print("\n".join(L))
