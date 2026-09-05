import bpy, os
from mathutils import Vector
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
OUT="d:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p07_strap_rig/fixcam/"
os.makedirs(OUT,exist_ok=True)
prev=bpy.context.window.scene; log=[]
try:
    bpy.context.window.scene=sc
    sc.render.engine='BLENDER_EEVEE_NEXT'
    sc.render.resolution_x=640; sc.render.resolution_y=360
    sc.render.film_transparent=False
    sc.eevee.taa_render_samples=24
    cam=bpy.data.objects.get("P07_FIXCHK_CAM")
    if cam is None:
        cd=bpy.data.cameras.new("P07_FIXCHK_CAM"); cam=bpy.data.objects.new("P07_FIXCHK_CAM",cd)
        sc.collection.objects.link(cam)
    cam.rotation_mode='QUATERNION'; cam.data.lens=32; cam.data.clip_start=0.01
    cam.data.dof.use_dof=False
    pos=Vector((1.75,-0.30,2.05)); tgt=Vector((0.10,-2.05,1.00))
    cam.location=pos
    cam.rotation_quaternion=(tgt-pos).normalized().to_track_quat('-Z','Z')
    old=sc.camera; sc.camera=cam
    for f in (1824,1872,1908,1944,1980,2016):
        sc.frame_set(f); sc.render.filepath=OUT+"g%05d"%f
        bpy.ops.render.render(write_still=True); log.append(str(f))
    sc.camera=old
finally:
    bpy.context.window.scene=prev
print("fixed-cam rendered "+", ".join(log))
