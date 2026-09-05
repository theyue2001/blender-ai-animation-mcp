import bpy, json, math
from mathutils import Vector, Matrix
SC=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
rep={}
C0=Vector((0.0,493.0,0.0)); R=8.5
DIRS={"A":Vector((0,0,1)),
      "C":Vector(( math.cos(math.radians(30)),0,-0.5)),
      "B":Vector((-math.cos(math.radians(30)),0,-0.5))}
DOME={"A":Vector((0,1,0)),"B":Vector((0,-1,0)),"C":Vector((0,0,-1))}
PERP={"A":Vector((0,0,1)),"B":Vector((0,0,1)),"C":Vector((0,1,0))}
TOCAM=Vector((0,-1,0))

def frame_from(cols):
    M=Matrix.Identity(3)
    for i,v in enumerate(cols):
        M[0][i],M[1][i],M[2][i]=v.x,v.y,v.z
    return M

ctr=bpy.data.objects["P08_RING_CTR"]
corners=[]
for k in "ABC":
    piv=bpy.data.objects["P08_PIV_%s"%k]; slv=bpy.data.objects["P08_SLV_%s"%k]
    d=DIRS[k].normalized(); u=DOME[k]; p=PERP[k]
    Ml=frame_from([u,p,u.cross(p)])
    Mw=frame_from([d,TOCAM,d.cross(TOCAM)])
    Ral=(Mw@Ml.transposed()).to_4x4()
    piv.rotation_mode='XYZ'; piv.rotation_euler=Ral.to_euler('XYZ')
    piv.location=d*R
    s=slv.scale[0]
    bb=[Vector(c) for c in slv.bound_box]
    c=(Vector((min(q[i] for q in bb) for i in range(3)))+Vector((max(q[i] for q in bb) for i in range(3))))/2.0
    slv.location=-c*s
    Mfull=(Matrix.Translation(C0) @ Matrix.Translation(d*R) @ Ral
           @ Matrix.Translation(-c*s) @ Matrix.Diagonal((s,s,s,1.0)))
    for q in bb: corners.append(Mfull@q)
    # verify the dome really points along d
    rep.setdefault("check",{})[k]={"rot_deg":[round(math.degrees(v),2) for v in Ral.to_euler('XYZ')],
        "dome_world":[round(v,3) for v in (Ral.to_3x3()@u)],
        "want":[round(v,3) for v in d],
        "tocam_axis":[round(v,3) for v in (Ral.to_3x3()@p)]}
    rep.setdefault("slv_keys",{})[k]=sorted(set(f.data_path for f in slv.animation_data.action.fcurves)) if (slv.animation_data and slv.animation_data.action) else None

# ---- camera ----
cam=bpy.data.objects["CAM_P08_02_Sleeves"]; LENS=35.0
ASP=SC.render.resolution_x/SC.render.resolution_y; MARGIN=0.90
xs=[-(q.x-C0.x) for q in corners]; zs=[q.z-C0.z for q in corners]
camX=C0.x-((min(xs)+max(xs))/2.0)*-1*-1
camX=C0.x+((min(xs)+max(xs))/2.0)*-1
camZ=C0.z+((min(zs)+max(zs))/2.0)
def fits(D):
    K=18.0/LENS
    for q in corners:
        depth=(C0.y+D)-q.y
        if depth<=0.1: return False
        hw=K*depth; hh=hw/ASP
        if abs(-(q.x-camX))>hw*MARGIN or abs(q.z-camZ)>hh*MARGIN: return False
    return True
lo,hi=5.0,400.0
for _ in range(60):
    m=(lo+hi)/2.0
    if fits(m): hi=m
    else: lo=m
D=hi
if cam.animation_data: cam.animation_data_clear()
if cam.data.animation_data: cam.data.animation_data_clear()
cam.location=(camX,C0.y+D,camZ); cam.rotation_mode='XYZ'
cam.rotation_euler=(math.radians(90),0,math.radians(180))
cam.data.lens=LENS; cam.data.dof.use_dof=True; cam.data.dof.aperture_fstop=4.0
cam.data.dof.focus_distance=D
rep["camera"]={"lens":LENS,"D":round(D,2),"loc":[round(camX,3),round(C0.y+D,2),round(camZ,3)],
               "screen_extent_x":[round(min(xs),2),round(max(xs),2)],
               "screen_extent_z":[round(min(zs),2),round(max(zs),2)]}
bpy.ops.wm.save_mainfile()
rep["saved"]=True
print(json.dumps(rep,indent=1))
