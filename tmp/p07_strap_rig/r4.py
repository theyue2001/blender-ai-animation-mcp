import bpy, math, os
from mathutils import Vector
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
OUT="d:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p07_strap_rig/mech_cad2/"
os.makedirs(OUT,exist_ok=True)
prev=bpy.context.window.scene; log=[]
try:
    bpy.context.window.scene=sc; sc.frame_set(1)
    sc.render.engine='BLENDER_EEVEE_NEXT'
    sc.render.resolution_x=900; sc.render.resolution_y=900
    sc.render.film_transparent=False; sc.view_settings.view_transform='Standard'
    sc.eevee.taa_render_samples=24
    cam=bpy.data.objects["P07_MECH_CAM"]; cam.data.clip_start=0.005; sc.camera=cam
    HW=["P07R_58.002","P07R_59.002","P07R_60.002","P07R_63.002","P07R_64.005"]
    ST=["P07_STRAP_UPPER","P07_STRAP_LOWER"]
    saved={}
    for o in sc.objects:
        if o.type=='MESH':
            saved[o.name]=o.hide_render; o.hide_render = o.name not in set(HW+ST)
    def shot(name,tgt,off,vis,lens):
        for n in HW+ST: bpy.data.objects[n].hide_render = n not in vis
        cam.data.lens=lens; t=Vector(tgt); p=t+Vector(off); cam.location=p
        cam.rotation_euler=(t-p).normalized().to_track_quat('-Z','Y').to_euler()
        sc.render.filepath=OUT+name; bpy.ops.render.render(write_still=True); log.append(name)
    A=set(HW+ST); NOPLATE=set(HW+ST)-{"P07R_58.002"}
    HWONLY=set(HW)-{"P07R_58.002"}
    B60=(-0.248,-1.534,1.017); B59=(0.267,-1.518,1.017)
    # front (+Y) views, outside the ring
    shot("60_front_all", B60, (-0.25, 0.85, 0.20), A, 50)
    shot("60_front_np",  B60, (-0.25, 0.85, 0.20), NOPLATE, 50)
    shot("60_front_hw",  B60, (-0.25, 0.85, 0.20), HWONLY, 50)
    shot("60_left_np",   B60, (-0.80, 0.35, 0.18), NOPLATE, 50)
    shot("60_up_np",     B60, (-0.10, 0.30, 0.80), NOPLATE, 50)
    shot("59_front_np",  B59, ( 0.25, 0.85, 0.20), NOPLATE, 50)
    shot("59_front_hw",  B59, ( 0.25, 0.85, 0.20), HWONLY, 50)
    shot("59_right_np",  B59, ( 0.80, 0.35, 0.18), NOPLATE, 50)
    shot("59_up_np",     B59, ( 0.10, 0.30, 0.80), NOPLATE, 50)
    shot("both_front",   (0.02,-1.52,1.0), (0.0, 1.6, 0.35), NOPLATE, 50)
    shot("both_top",     (0.02,-1.52,1.0), (0.0, 0.9, 1.10), NOPLATE, 50)
    shot("low_front",    (0.02,-1.51,0.24),(0.0, 1.3, 0.30), NOPLATE, 50)
    for k,v in saved.items(): bpy.data.objects[k].hide_render=v
finally:
    bpy.context.window.scene=prev
print("OK: "+", ".join(log))
