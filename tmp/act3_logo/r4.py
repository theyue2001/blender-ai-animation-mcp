import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT = r"D:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\act3_logo"
L=[]
sc = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene
pfr = sc.frame_current
try:
    bpy.context.window.scene = sc
    cam = sc.camera
    for f in (864, 950, 1050, 1150, 1248, 1340, 1396):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        row=[]
        for nm in ("X5_DECAL_NITE_R1_Logo","WRN_DECAL_NITE_R1_Logo"):
            o=bpy.data.objects[nm]
            oe=o.evaluated_get(dg); mm=oe.to_mesh()
            ws=[oe.matrix_world @ v.co for v in mm.vertices]; oe.to_mesh_clear()
            ctr=sum(ws,Vector())/len(ws)
            nrm=Vector()
            for p in o.data.polygons: nrm += (oe.matrix_world.to_3x3() @ p.normal)
            nrm.normalize()
            xs=[world_to_camera_view(sc,cam,v).x for v in ws]
            ys=[1-world_to_camera_view(sc,cam,v).y for v in ws]
            facing = nrm.dot((cam.matrix_world.translation-ctr).normalized())
            row.append("%s x=%.3f..%.3f y=%.3f..%.3f facing=%+.2f hide_r=%s" % (
                nm.split('_')[0], min(xs),max(xs),min(ys),max(ys), facing, oe.hide_render))
        L.append("f%-5d  %s   |   %s" % (f, row[0], row[1]))
finally:
    sc.frame_set(pfr)
    bpy.context.window.scene = prev
print("\n".join(L))
