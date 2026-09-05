import bpy, json, math
import numpy as np
from mathutils import Vector, Matrix
SC=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
PF=r"C:\Users\mountain\AppData\Local\Temp\claude\d-----26-0825----3D---VScode\87e289ce-469b-4c17-8671-68b6cfdb67b0\scratchpad\ring_params.json"
P=json.load(open(PF))
C0=Vector(P["C0"]); R=P["R"]; DP={k:Vector(v).normalized() for k,v in P["DP"].items()}
LENS=35.0; ASP=SC.render.resolution_x/SC.render.resolution_y; MARGIN=0.96
rep={}; hull=[]
for k in "ABC":
    slv=bpy.data.objects["P08_SLV_%s"%k]; piv=bpy.data.objects["P08_PIV_%s"%k]
    me=slv.data; n=len(me.vertices)
    arr=np.empty(n*3,dtype=np.float32); me.vertices.foreach_get("co",arr)
    V=arr.reshape(-1,3)[::29]
    mn=V.min(axis=0); mx=V.max(axis=0); ext=mx-mn
    ax=int(np.argmax(ext)); a,b=[i for i in range(3) if i!=ax]
    lo,hi=float(mn[ax]),float(mx[ax]); L=hi-lo; NS=16
    rad=np.hypot(V[:,a],V[:,b]); idx=np.clip(((V[:,ax]-lo)/L*NS).astype(int),0,NS-1)
    prof=[float(rad[idx==s].max()) if np.any(idx==s) else 0.0 for s in range(NS)]
    pts=[]
    for s in range(NS):
        yc=lo+L*(s+0.5)/NS; rr=prof[s]
        for j in range(20):
            th=2*math.pi*j/20.0
            q=[0.0,0.0,0.0]; q[ax]=yc; q[a]=rr*math.cos(th); q[b]=rr*math.sin(th)
            pts.append(Vector(q))
    sc_=slv.scale[0]; c=Vector(((mn+mx)/2.0).tolist())
    Ral=piv.rotation_euler.to_matrix().to_4x4()
    base=Matrix.Translation(DP[k]*R)@Ral@Matrix.Translation(-c*sc_)@Matrix.Diagonal((sc_,sc_,sc_,1.0))
    for ang in (0,6,12,19,26,32,38):
        Mw=Matrix.Translation(C0)@Matrix.Rotation(math.radians(ang),4,'Y')@base
        for q in pts: hull.append(Mw@q)
    rep.setdefault("world_radius_max",{})[k]=round(max(prof)*sc_,3)
    rep.setdefault("world_len",{})[k]=round(L*sc_,3)
xs=[-(q.x-C0.x) for q in hull]; zs=[q.z-C0.z for q in hull]
camX=C0.x-((min(xs)+max(xs))/2.0); camZ=C0.z+((min(zs)+max(zs))/2.0)
def fits(D):
    K=18.0/LENS
    for q in hull:
        dep=(C0.y+D)-q.y
        if dep<=0.1: return False
        hw=K*dep; hh=hw/ASP
        if abs(-(q.x-camX))>hw*MARGIN or abs(q.z-camZ)>hh*MARGIN: return False
    return True
lo_,hi_=5.0,400.0
for _ in range(60):
    m=(lo_+hi_)/2.0
    if fits(m): hi_=m
    else: lo_=m
D_END=hi_; D_START=D_END*1.09
cam=bpy.data.objects["CAM_P08_02_Sleeves"]
for fc in cam.animation_data.action.fcurves:
    if fc.data_path=='location':
        for kp in fc.keyframe_points:
            if fc.array_index==0: kp.co[1]=camX
            elif fc.array_index==2: kp.co[1]=camZ
            else: kp.co[1]=(C0.y+D_START) if kp.co[0]<2600 else (C0.y+D_END)
        fc.update()
for fc in cam.data.animation_data.action.fcurves:
    if fc.data_path=='dof.focus_distance':
        for kp in fc.keyframe_points: kp.co[1]=D_START if kp.co[0]<2600 else D_END
        fc.update()
rep["camera"]={"D_end_old":round(P["D_END"],2),"D_end_new":round(D_END,2),
               "D_start_new":round(D_START,2),"camX":round(camX,3),"camZ":round(camZ,3),
               "hull_screen_x":[round(min(xs),2),round(max(xs),2)],
               "hull_screen_z":[round(min(zs),2),round(max(zs),2)]}
P["D_END"]=D_END; P["D_START"]=D_START; P["camX"]=camX; P["camZ"]=camZ
json.dump(P,open(PF,"w"))
bpy.ops.wm.save_mainfile()
print(json.dumps(rep,indent=1))
