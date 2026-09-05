import bpy, os
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
OUT="d:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p07_strap_rig/preview/"
os.makedirs(OUT,exist_ok=True)
prev=bpy.context.window.scene
S={}
try:
    bpy.context.window.scene=sc
    r=sc.render
    S=dict(eng=r.engine,rx=r.resolution_x,ry=r.resolution_y,pct=r.resolution_percentage,
           fp=r.filepath,ff=r.image_settings.file_format,fs=sc.frame_start,fe=sc.frame_end,
           ft=r.film_transparent,vt=sc.view_settings.view_transform,sm=sc.eevee.taa_render_samples)
    r.engine='BLENDER_EEVEE_NEXT'
    r.resolution_x=960; r.resolution_y=540; r.resolution_percentage=100
    r.film_transparent=False
    sc.view_settings.view_transform='Standard'
    sc.eevee.taa_render_samples=16
    r.image_settings.file_format='FFMPEG'
    r.ffmpeg.format='MPEG4'; r.ffmpeg.codec='H264'
    r.ffmpeg.constant_rate_factor='HIGH'
    r.ffmpeg.ffmpeg_preset='GOOD'
    r.ffmpeg.audio_codec='NONE'
    sc.frame_start=1824; sc.frame_end=2016
    r.filepath=OUT+"P07_1_16_to_1_24_"
    bpy.ops.render.render(animation=True)
    print("rendered preview to",r.filepath)
finally:
    if S:
        r=sc.render
        r.engine=S['eng']; r.resolution_x=S['rx']; r.resolution_y=S['ry']
        r.resolution_percentage=S['pct']; r.filepath=S['fp']
        r.image_settings.file_format=S['ff']; sc.frame_start=S['fs']; sc.frame_end=S['fe']
        r.film_transparent=S['ft']; sc.view_settings.view_transform=S['vt']
        sc.eevee.taa_render_samples=S['sm']
    bpy.context.window.scene=prev
