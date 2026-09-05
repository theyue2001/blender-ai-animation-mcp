import bpy, os
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
OUT="d:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p07_strap_rig/shot/"
os.makedirs(OUT,exist_ok=True)
prev=bpy.context.window.scene; log=[]
try:
    bpy.context.window.scene=sc
    sc.render.engine='BLENDER_EEVEE_NEXT'
    sc.render.resolution_x=640; sc.render.resolution_y=360; sc.render.resolution_percentage=100
    sc.render.film_transparent=False
    sc.render.image_settings.file_format='PNG'
    sc.eevee.taa_render_samples=24
    sc.camera=bpy.data.objects["P07_SHOT_CAM"]
    for f in (1824,1841,1866,1893,1894,1916,1938,1955,1956,1975,1991,2016):
        sc.frame_set(f)
        sc.render.filepath=OUT+"f%05d"%f
        bpy.ops.render.render(write_still=True); log.append(str(f))
finally:
    bpy.context.window.scene=prev
print("rendered "+", ".join(log))
