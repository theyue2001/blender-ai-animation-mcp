import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
X0,X1,Y0,Y1 = 1256,1500,280,495
try:
    win.scene=sc; sc.frame_set(1434)
    dg=bpy.context.evaluated_depsgraph_get()
    cam=sc.camera.evaluated_get(dg)
    names=["X5_1.002","X5_2.002","X5_4.002","X5_6.002","X5_8.002","X5_10.002","X5_12.002","X5_16_0.002"]
    T={}
    for n in names:
        oe=sc.objects[n].evaluated_get(dg)
        bm=bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm,faces=bm.faces); bm.faces.ensure_lookup_table()
        T[n]=(BVHTree.FromBMesh(bm), bm)
    print("%-11s %-11s %6s %6s %8s %8s  %s" % ("A","B","tris","inBox","med.ang","copl%","world Z / px box"))
    hits=[]
    for i in range(len(names)):
        for j in range(i+1,len(names)):
            a,b=names[i],names[j]
            ov=T[a][0].overlap(T[b][0])
            if not ov: continue
            bmA=T[a][1]; bmB=T[b][1]
            inbox=0; angs=[]; zs=[]; pxs=[]
            for fa,fb in ov:
                f=bmA.faces[fa]; c=f.calc_center_median()
                co=world_to_camera_view(sc,cam,c)
                px,py = co.x*1920,(1-co.y)*1080
                d=max(-1.0,min(1.0,f.normal.normalized().dot(bmB.faces[fb].normal.normalized())))
                angs.append(math.degrees(math.acos(abs(d)))); zs.append(c.z)
                if X0<=px<=X1 and Y0<=py<=Y1:
                    inbox+=1; pxs.append((px,py))
            angs.sort()
            copl=100.0*sum(1 for x in angs if x<5.0)/len(angs)
            tag = "  <<< IN CIRCLE" if inbox>20 else ""
            print("%-11s %-11s %6d %6d %8.1f %7.0f%%  Z %.3f..%.3f%s" % (
                a.replace("X5_",""), b.replace("X5_",""), len(ov), inbox,
                angs[len(angs)//2], copl, min(zs), max(zs), tag))
finally:
    win.scene=prev
