import bpy, json, math
from mathutils import Vector, Matrix
SC=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
TILT=math.radians(52.0); C0=Vector((0.0,493.0,0.0)); R=7.2
TOCAM=Vector((0,1,0)); LENS=35.0
ASP=SC.render.resolution_x/SC.render.resolution_y; MARGIN=0.90
RING_MAX=math.radians(38.0)
DIRS={"A":Vector((0,0,1)),
      "C":Vector(( math.cos(math.radians(30)),0,-0.5)),
      "B":Vector((-math.cos(math.radians(30)),0,-0.5))}
DOME={"A":Vector((0,1,0)),"B":Vector((0,-1,0)),"C":Vector((0,0,-1))}
PERP={"A":Vector((0,0,1)),"B":Vector((0,0,1)),"C":Vector((0,1,0))}
def frame_from(cols):
    M=Matrix.Identity(3)
    for i,v in enumerate(cols): M[0][i],M[1][i],M[2][i]=v.x,v.y,v.z
    return M
rep={"tilt":52.0,"R":R}
ctr=bpy.data.objects["P08_RING_CTR"]; ctr.location=C0
DP={}; corners=[]
for k in "ABC":
    piv=bpy.data.objects["P08_PIV_%s"%k]; slv=bpy.data.objects["P08_SLV_%s"%k]
    d=(DIRS[k].normalized()*math.cos(TILT)+TOCAM*math.sin(TILT)).normalized(); DP[k]=d
    e2=(TOCAM-d*TOCAM.dot(d)).normalized(); e3=d.cross(e2)
    u=DOME[k]; p=PERP[k]
    Ral=(frame_from([d,e2,e3])@frame_from([u,p,u.cross(p)]).transposed()).to_4x4()
    piv.rotation_mode='XYZ'; piv.rotation_euler=Ral.to_euler('XYZ'); piv.location=d*R
    s=slv.scale[0]
    bb=[Vector(c) for c in slv.bound_box]
    c=(Vector((min(q[i] for q in bb) for i in range(3)))+Vector((max(q[i] for q in bb) for i in range(3))))/2.0
    slv.location=-c*s
    base=(Matrix.Translation(d*R)@Ral@Matrix.Translation(-c*s)@Matrix.Diagonal((s,s,s,1.0)))
    for ang in (0,8,16,24,32,38):          # fit must survive the ring rotation
        Mw=Matrix.Translation(C0)@Matrix.Rotation(math.radians(ang),4,'Y')@base
        for q in bb: corners.append(Mw@q)
    rep.setdefault("dir",{})[k]=[round(v,3) for v in d]
xs=[-(q.x-C0.x) for q in corners]; zs=[q.z-C0.z for q in corners]
camX=C0.x-((min(xs)+max(xs))/2.0); camZ=C0.z+((min(zs)+max(zs))/2.0)
def fits(D):
    K=18.0/LENS
    for q in corners:
        dep=(C0.y+D)-q.y
        if dep<=0.1: return False
        hw=K*dep; hh=hw/ASP
        if abs(-(q.x-camX))>hw*MARGIN or abs(q.z-camZ)>hh*MARGIN: return False
    return True
lo,hi=5.0,400.0
for _ in range(60):
    m=(lo+hi)/2.0
    if fits(m): hi=m
    else: lo=m
D_END=hi; D_START=D_END*1.09
rep["camera"]={"D_end":round(D_END,2),"D_start":round(D_START,2),
               "loc_end":[round(camX,3),round(C0.y+D_END,2),round(camZ,3)],
               "sx":[round(min(xs),2),round(max(xs),2)],"sz":[round(min(zs),2),round(max(zs),2)]}
json.dump({"DP":{k:list(DP[k]) for k in DP},"C0":list(C0),"R":R,
           "D_END":D_END,"D_START":D_START,"camX":camX,"camZ":camZ,
           "RING_MAX":RING_MAX},
          open(r"C:\Users\mountain\AppData\Local\Temp\claude\d-----26-0825----3D---VScode\87e289ce-469b-4c17-8671-68b6cfdb67b0\scratchpad\ring_params.json","w"))
bpy.ops.wm.save_mainfile()
print(json.dumps(rep,indent=1))
