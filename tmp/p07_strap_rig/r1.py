import bpy, math
from mathutils import Vector, Matrix
SN="05_SCN_P07_STRAP_RIG"
sc=bpy.data.scenes[SN]
cam=bpy.data.objects["P07_QA_CAM"]
OUT=r"d:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p07_strap_rig/"
def look(cam, eye, tgt):
    d=(Vector(tgt)-Vector(eye)).normalized()
    up=Vector((0,0,1))
    if abs(d.dot(up))>0.999: up=Vector((0,1,0))
    r=d.cross(up).normalized(); u=r.cross(d).normalized()
    M=Matrix(((r.x,u.x,-d.x,eye[0]),(r.y,u.y,-d.y,eye[1]),(r.z,u.z,-d.z,eye[2]),(0,0,0,1)))
    cam.matrix_world=M
C=(0.05,-2.20,0.65)
views={
 "s_front":((0.05,2.6,0.85),(0.05,-2.2,0.75),60),
 "s_top":((0.05,-2.19,5.2),(0.05,-2.2,0.7),50),
 "s_left":((-4.6,-2.2,1.0),(0.05,-2.2,0.7),60),
 "s_right":((4.6,-2.2,1.0),(0.05,-2.2,0.7),60),
 "s_back":((0.05,-7.0,1.0),(0.05,-2.2,0.7),60),
 "s_q34":((2.6,0.9,2.2),(0.05,-2.2,0.7),55),
 "s_buckle_up":((0.05,0.55,1.05),(0.05,-1.5,1.0),85),
 "s_buckle_lo":((0.05,0.55,0.30),(0.05,-1.5,0.25),85),
}
prev=bpy.context.window.scene
prevfs={s.name:s.frame_current for s in bpy.data.scenes}
try:
    bpy.context.window.scene=sc
    sc.render.resolution_x=900; sc.render.resolution_y=900
    for k,(eye,tgt,lens) in views.items():
        cam.data.lens=lens; look(cam,eye,tgt)
        sc.render.filepath=OUT+k+".png"
        bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=prev
    for s in bpy.data.scenes:
        s.frame_current=prevfs[s.name]
print("rendered", list(views))
