import bpy, json
from mathutils import Vector, Matrix
sc=[s for s in bpy.data.scenes if "CAM_Opening_Silhouette" in s.objects][0]
cam=sc.objects["CAM_Opening_Silhouette"]
tgt=bpy.data.objects["CTRL_Opening_Silhouette_Target"].matrix_basis.translation
fcs=sorted([fc for fc in cam.animation_data.action.fcurves if fc.data_path=="location"],key=lambda x:x.array_index)
lens=cam.data.lens; sw=cam.data.sensor_width; W,H=1920,1080
tx=(sw/2)/lens; ty=tx*H/W
def wm(o):
    m=o.matrix_basis.copy(); cur=o
    while cur.parent is not None:
        m=cur.parent.matrix_basis @ cur.matrix_parent_inverse @ m; cur=cur.parent
    return m
o=bpy.data.objects["49.002"]; M=wm(o)
pts=[M @ Vector(v) for v in o.bound_box]
out={}
for F in [198,250,300,350,400,426,450]:
    loc=Vector([f.evaluate(F) for f in fcs])
    q=(tgt-loc).to_track_quat('-Z','Y')
    Minv=(Matrix.Translation(loc) @ q.to_matrix().to_4x4()).inverted()
    xs=[];ys=[]
    for p in pts:
        v=Minv @ p
        if v.z>=-1e-6: continue
        xs.append(((v.x/-v.z)/tx*0.5+0.5)*W); ys.append((1-((v.y/-v.z)/ty*0.5+0.5))*H)
    out[F]=[round(min(xs)),round(min(ys)),round(max(xs)),round(max(ys))]
print(json.dumps(out))
