import bpy, json, math
from mathutils import Vector, Matrix
PF=r"C:\Users\mountain\AppData\Local\Temp\claude\d-----26-0825----3D---VScode\87e289ce-469b-4c17-8671-68b6cfdb67b0\scratchpad\ring_params.json"
P=json.load(open(PF))
C0=Vector(P["C0"]); DP={k:Vector(v).normalized() for k,v in P["DP"].items()}
TOCAM=Vector((0,1,0)); DOT_MAX=14.0
SC=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
LENS=35.0; ASP=SC.render.resolution_x/SC.render.resolution_y
camY=C0.y+P["D_END"]; camX=P["camX"]; camZ=P["camZ"]
rep={}
for k in "ABC":
    d=DP[k]; e2=(TOCAM-d*TOCAM.dot(d)).normalized(); e3=d.cross(e2)
    tr=bpy.data.objects["P08_SLVTRAIL_%s"%k]
    tr.matrix_world=Matrix.Identity(4)
    sp=tr.data.splines[0]; N=len(sp.points)
    for i,pt in enumerate(sp.points):
        u=i/(N-1.0)
        w=C0+d*(DOT_MAX*u)+e3*(0.09*DOT_MAX*math.sin(math.pi*u))
        pt.co=(w.x,w.y,w.z,1.0)
    tr.data.update_tag()
    # verify the dot tip stays inside frame
    tip=C0+d*DOT_MAX
    dep=camY-tip.y; hw=(18.0/LENS)*dep; hh=hw/ASP
    sx=-(tip.x-camX); sz=tip.z-camZ
    rep[k]={"tip_screen_frac":[round(abs(sx)/hw,3),round(abs(sz)/hh,3)],
            "tip_world":[round(v,2) for v in tip]}
    # soften the bloom a touch
    dot=bpy.data.objects["P08_SLVDOT_%s"%k]
    for fc in dot.animation_data.action.fcurves:
        if fc.data_path=='scale':
            for kp in fc.keyframe_points:
                if abs(kp.co[1]-2.6)<1e-6: kp.co[1]=2.15
            fc.update()
    dm=dot.material_slots[0].material
    for fc in dm.node_tree.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            if abs(kp.co[1]-430.0)<1e-6: kp.co[1]=340.0
        fc.update()
bpy.ops.wm.save_mainfile()
rep["dot_max"]=DOT_MAX; rep["saved"]=True
print(json.dumps(rep,indent=1))
