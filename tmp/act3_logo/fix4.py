import bpy
L=[]
src = bpy.data.materials["MAT_P01_CONTROL_BUTTONS"]
sb  = next(n for n in src.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
dst = bpy.data.materials["MAT_P05W_Control_Plate"]
db  = next(n for n in dst.node_tree.nodes if n.type=='BSDF_PRINCIPLED')

# scene 01's settled (post-frame-320) button look
vals = {'Base Color':(0.3414,0.3532,0.4023,1.0), 'Metallic':1.0, 'Roughness':0.66,
        'Specular IOR Level':1.0, 'Coat Weight':0.0, 'Coat Roughness':0.03}
before = {k:(tuple(round(float(x),4) for x in db.inputs[k].default_value) if hasattr(db.inputs[k].default_value,'__len__') else round(float(db.inputs[k].default_value),4)) for k in vals}
for k,v in vals.items():
    db.inputs[k].default_value = v
L.append("MAT_P05W_Control_Plate Principled")
L.append("  before: %s" % before)
L.append("  after : %s" % {k:(tuple(round(float(x),4) for x in v) if hasattr(v,'__len__') else v) for k,v in vals.items()})
L.append("  press rig intact: %s" % sorted(n.name for n in dst.node_tree.nodes if n.name in ('KEY_UP','RAD','ZGATE','FACE_POW','FACE_MOD','LWK','Emission','Add Shader')))
kf = dst.node_tree.animation_data.action.fcurves[0]
L.append("  KEY_UP fcurve keys=%d" % len(kf.keyframe_points))
bpy.ops.wm.save_mainfile()
L.append("SAVED")
print("\n".join(L))
