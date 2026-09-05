import bpy, math, os
from mathutils import Vector
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
OUT="d:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p07_strap_rig/mech_wb/"
os.makedirs(OUT,exist_ok=True)
prev=bpy.context.window.scene; log=[]
try:
    bpy.context.window.scene=sc; sc.frame_set(1)
    eng=sc.render.engine
    sc.render.engine='BLENDER_WORKBENCH'
    sh=sc.display.shading
    sh.light='STUDIO'; sh.color_type='SINGLE'; sh.single_color=(0.55,0.56,0.58)
    sh.show_cavity=True; sh.cavity_type='BOTH'; sh.show_object_outline=True
    sc.render.resolution_x=800; sc.render.resolution_y=800
    sc.display.render_aa='16'
    cam=bpy.data.objects["P07_MECH_CAM"]; sc.camera=cam
    cam.data.type='ORTHO'; cam.data.clip_start=0.001
    HW=["P07R_58.002","P07R_59.002","P07R_60.002","P07R_63.002","P07R_64.005"]
    ST=["P07_STRAP_UPPER","P07_STRAP_LOWER"]
    saved={}
    for o in sc.objects:
        if o.type=='MESH': saved[o.name]=o.hide_render; o.hide_render=True
    def shot(name,tgt,dirv,up,scale,vis):
        for n in HW+ST: bpy.data.objects[n].hide_render = n not in vis
        cam.data.ortho_scale=scale
        t=Vector(tgt); d=Vector(dirv).normalized(); cam.location=t-d*3.0
        cam.rotation_euler=d.to_track_quat('-Z',up).to_euler()
        sc.render.filepath=OUT+name; bpy.ops.render.render(write_still=True); log.append(name)
    for part,ctr in (("60",(-0.248,-1.534,1.017)),("59",(0.267,-1.518,1.017))):
        P={"P07R_%s.002"%part} if part=="60" else {"P07R_59.002"}
        PS=P|{"P07_STRAP_UPPER"}
        for vn,vis in (("hw",P),("st",PS)):
            shot("%s_%s_FRONT"%(part,vn),ctr,(0,-1,0),'Z',0.60,vis)
            shot("%s_%s_LEFT"%(part,vn), ctr,(1,0,0), 'Z',0.60,vis)
            shot("%s_%s_TOP"%(part,vn),  ctr,(0,0,-1),'Y',0.60,vis)
    shot("63_hw_FRONT",(-0.247,-1.514,0.241),(0,-1,0),'Z',0.35,{"P07R_63.002"})
    shot("63_hw_LEFT", (-0.247,-1.514,0.241),(1,0,0), 'Z',0.35,{"P07R_63.002"})
    shot("63_st_LEFT", (-0.247,-1.514,0.241),(1,0,0), 'Z',0.35,{"P07R_63.002","P07_STRAP_LOWER"})
    shot("63_st_TOP",  (-0.247,-1.514,0.241),(0,0,-1),'Y',0.35,{"P07R_63.002","P07_STRAP_LOWER"})
    for k,v in saved.items(): bpy.data.objects[k].hide_render=v
    sc.render.engine=eng; cam.data.type='PERSP'
finally:
    bpy.context.window.scene=prev
print("OK: "+", ".join(log))
