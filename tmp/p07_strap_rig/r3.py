import bpy, math, os
from mathutils import Vector
SN="05_SCN_P07_STRAP_RIG"
sc=bpy.data.scenes[SN]
OUT="d:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p07_strap_rig/mech_cad/"
os.makedirs(OUT,exist_ok=True)
prev=bpy.context.window.scene
log=[]
try:
    bpy.context.window.scene=sc
    sc.frame_set(1)
    sc.render.engine='BLENDER_EEVEE_NEXT'
    sc.render.resolution_x=900; sc.render.resolution_y=900; sc.render.resolution_percentage=100
    sc.render.film_transparent=False
    sc.render.image_settings.file_format='PNG'
    sc.view_settings.view_transform='Standard'
    sc.eevee.taa_render_samples=16

    cam=bpy.data.objects.get("P07_MECH_CAM")
    if cam is None:
        cd=bpy.data.cameras.new("P07_MECH_CAM"); cam=bpy.data.objects.new("P07_MECH_CAM",cd)
        sc.collection.objects.link(cam)
    cam.data.lens=70; cam.data.clip_start=0.005
    sc.camera=cam

    # keep only hardware + rig straps visible
    KEEP={"P07R_58.002","P07R_59.002","P07R_60.002","P07R_63.002","P07R_64.005",
          "P07R_GEO_NITE_R1_Rear_Central_Pillar_Emboss","P07_STRAP_UPPER","P07_STRAP_LOWER"}
    saved={}
    for o in sc.objects:
        if o.type=='MESH':
            saved[o.name]=o.hide_render
            o.hide_render = o.name not in KEEP

    def shot(name, tgt, off, straps=True, lens=70):
        for s in ("P07_STRAP_UPPER","P07_STRAP_LOWER"):
            bpy.data.objects[s].hide_render = not straps
        cam.data.lens=lens
        t=Vector(tgt); p=t+Vector(off)
        cam.location=p
        d=(t-p).normalized()
        cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
        sc.render.filepath=OUT+name
        bpy.ops.render.render(write_still=True)
        log.append(name)

    B60=(-0.248,-1.534,1.017); B59=(0.267,-1.518,1.017); BK=(0.049,-1.60,0.72)
    for st,sfx in ((True,"_S"),(False,"_H")):
        shot("60_out"+sfx, B60, (-0.30,-0.55, 0.16), st, 85)
        shot("60_top"+sfx, B60, (-0.10,-0.30, 0.55), st, 85)
        shot("59_out"+sfx, B59, ( 0.34,-0.55, 0.16), st, 85)
        shot("59_top"+sfx, B59, ( 0.10,-0.30, 0.55), st, 85)
        shot("back"+sfx,   BK,  ( 0.20,-1.60, 0.55), st, 50)
        shot("low63"+sfx,  (-0.247,-1.514,0.241), (-0.30,-0.45,0.16), st, 90)
    for k,v in saved.items(): bpy.data.objects[k].hide_render=v
finally:
    bpy.context.window.scene=prev
print("RENDERED: "+", ".join(log))
