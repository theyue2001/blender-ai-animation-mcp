import bpy
L=[]
KEY=('Base Color','Metallic','Roughness','Specular IOR Level','Coat Weight','Emission Color','Emission Strength')
def dump(mn):
    m=bpy.data.materials.get(mn)
    if not m: L.append("%s MISSING"%mn); return
    nt=m.node_tree
    L.append("=== %s (users=%d anim=%s nodes=%d) ===" % (m.name,m.users,bool(nt.animation_data and nt.animation_data.action),len(nt.nodes)))
    if nt.animation_data and nt.animation_data.action:
        for fc in nt.animation_data.action.fcurves:
            L.append("   FCU %s : %s" % (fc.data_path[:66], [(int(k.co[0]),round(k.co[1],3)) for k in fc.keyframe_points][:10]))
    out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
    L.append("   OUTPUT <- %s" % (out.inputs['Surface'].links[0].from_node.name if out.inputs['Surface'].is_linked else None))
    for n in nt.nodes:
        if n.type=='BSDF_PRINCIPLED':
            v=[]
            for k in KEY:
                if k in n.inputs:
                    i=n.inputs[k]
                    if i.is_linked: v.append("%s<-%s"%(k,i.links[0].from_node.name))
                    else:
                        d=i.default_value
                        d=tuple(round(float(x),4) for x in d) if hasattr(d,'__len__') else round(float(d),4)
                        v.append("%s=%s"%(k,d))
            L.append("   [PRINCIPLED %s] %s" % (n.name," ".join(v)))
        elif n.type in ('MIX_SHADER','ADD_SHADER','MIX','VALTORGB','VALUE','MAP_RANGE','MATH','TEX_IMAGE','ATTRIBUTE','SEPXYZ','TEX_COORD','LAYER_WEIGHT'):
            ins=[]
            for i in n.inputs:
                if i.is_linked: ins.append("%s<-%s.%s"%(i.name,i.links[0].from_node.name,i.links[0].from_socket.name))
                else:
                    d=getattr(i,'default_value',None)
                    if hasattr(d,'__len__') and not isinstance(d,str): d=tuple(round(float(x),3) for x in d)
                    elif isinstance(d,float): d=round(d,3)
                    ins.append("%s=%s"%(i.name,d))
            extra=""
            if n.type=='VALUE': extra=" out=%.4f"%n.outputs[0].default_value
            if n.type=='VALTORGB': extra=" stops=%s"%[(round(e.position,3),tuple(round(float(x),3) for x in e.color)) for e in n.color_ramp.elements]
            if n.type=='TEX_IMAGE': extra=" image=%s"%(n.image.name if n.image else None)
            L.append("   [%s %s]%s %s" % (n.type,n.name,extra," | ".join(ins)[:200]))
    L.append("")
dump("MAT_P01_CONTROL_BUTTONS")
dump("MAT_P05W_Control_Plate")
dump("MAT_P05W2_SHOT1_CONTROL_38_0.002_0")
print("\n".join(L))
