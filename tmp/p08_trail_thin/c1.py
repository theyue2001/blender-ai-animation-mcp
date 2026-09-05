import bpy, json, math
from mathutils import Vector, Matrix, Quaternion
SC=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
rep={}

C0=Vector((0.0,493.0,0.0))          # ring array centre
R=8.5                                # radius of each sleeve's bbox centre
# screen: world +X = screen LEFT, world +Z = screen UP (cam rot 90,0,180)
DIRS={"A":Vector((0,0,1)),                                   # screen up
      "C":Vector(( math.cos(math.radians(30)),0,-0.5)),      # world +X,-Z = screen DOWN-LEFT
      "B":Vector((-math.cos(math.radians(30)),0,-0.5))}      # world -X,-Z = screen DOWN-RIGHT
DOME={"A":Vector((0,1,0)),"B":Vector((0,-1,0)),"C":Vector((0,0,-1))}

# ---- ring centre empty ----
ctr=bpy.data.objects.get("P08_RING_CTR")
if ctr is None:
    ctr=bpy.data.objects.new("P08_RING_CTR",None)
    ctr.empty_display_type='PLAIN_AXES'; ctr.empty_display_size=6.0
    bpy.data.collections["P08_SLEEVES"].objects.link(ctr)
ctr.parent=None
ctr.location=C0; ctr.rotation_mode='XYZ'; ctr.rotation_euler=(0,0,0); ctr.scale=(1,1,1)
if ctr.animation_data: ctr.animation_data_clear()

corners=[]
for k in "ABC":
    piv=bpy.data.objects["P08_PIV_%s"%k]
    slv=bpy.data.objects["P08_SLV_%s"%k]
    d=DIRS[k].normalized(); u=DOME[k]
    Ral=u.rotation_difference(d).to_matrix().to_4x4()

    # pivot: child of ring centre, at radius R along d, oriented dome-outward
    if piv.animation_data: piv.animation_data_clear()
    piv.parent=ctr; piv.matrix_parent_inverse=Matrix.Identity(4)
    piv.rotation_mode='XYZ'
    piv.location=d*R
    piv.rotation_euler=Ral.to_euler('XYZ')
    piv.scale=(1,1,1)

    # sleeve: child of pivot, bbox centre pinned to the pivot origin
    s=slv.scale[0]
    bb=[Vector(c) for c in slv.bound_box]
    c=(Vector((min(p[i] for p in bb) for i in range(3)))+Vector((max(p[i] for p in bb) for i in range(3))))/2.0
    slv.parent=piv; slv.matrix_parent_inverse=Matrix.Identity(4)
    slv.rotation_mode='XYZ'; slv.rotation_euler=(0,0,0)
    slv.location=-c*s
    slv.scale=(s,s,s)

    # analytic world matrix -> bbox corners (no depsgraph)
    Mw=(Matrix.Translation(C0) @ Matrix.Identity(4)
        @ Matrix.Translation(d*R) @ Ral
        @ Matrix.Translation(-c*s) @ Matrix.Diagonal((s,s,s,1.0)))
    for p in bb: corners.append(Mw@p)
    rep.setdefault("layout",{})[k]={"dir_world":[round(v,3) for v in d],
        "pivot_loc":[round(v,3) for v in (d*R)],
        "rot_deg":[round(math.degrees(v),2) for v in Ral.to_euler('XYZ')],
        "scale":round(s,5),"bbox_centre_local":[round(v,3) for v in c]}

# ---- solve camera framing ----
cam=bpy.data.objects["CAM_P08_02_Sleeves"]
LENS=35.0; ASP=SC.render.resolution_x/SC.render.resolution_y; MARGIN=0.90
# screen coords: sx = -(x - camx), sy = (z - camz); depth = camy - y
xs=[-(p.x-C0.x) for p in corners]; zs=[p.z-C0.z for p in corners]; ys=[p.y for p in corners]
sx_c=(min(xs)+max(xs))/2.0; sz_c=(min(zs)+max(zs))/2.0
rep["array_screen_extent"]={"x":[round(min(xs),2),round(max(xs),2)],
                            "z":[round(min(zs),2),round(max(zs),2)],
                            "y_depth":[round(min(ys),2),round(max(ys),2)],
                            "centre_offset":[round(sx_c,3),round(sz_c,3)]}
camX=C0.x - sx_c*(-1)   # sx = -(x-camx) -> camx = x + sx ; centre sx_c at 0 => camx = C0.x - sx_c
camX=C0.x + sx_c*0 - sx_c*0  # keep on axis; handled below
camX=C0.x - (-sx_c)
camZ=C0.z + sz_c
def fits(D):
    K=(18.0/LENS)
    for p in corners:
        depth=(C0.y+D)-p.y
        if depth<=0.1: return False
        hw=K*depth; hh=hw/ASP
        if abs(-(p.x-camX))>hw*MARGIN or abs(p.z-camZ)>hh*MARGIN: return False
    return True
lo,hi=5.0,400.0
for _ in range(60):
    mid=(lo+hi)/2.0
    if fits(mid): hi=mid
    else: lo=mid
D=hi
rep["camera_solve"]={"lens":LENS,"distance":round(D,2),"cam_loc":[round(camX,3),round(C0.y+D,2),round(camZ,3)],
                     "margin":MARGIN}
print(json.dumps(rep,indent=1))
