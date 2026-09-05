import bpy, os, math, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    ob = sc.objects["X5_16_0.002"]; me = ob.data; mw = ob.matrix_world
    cam = sc.camera.evaluated_get(dg)
    bk = {int(k): Vector(v) for k,v in json.load(open(os.path.join(OUT,"vert_backup.json")))["coords"].items()}
    def newell(pts):
        n = Vector((0,0,0))
        for i in range(len(pts)):
            a = pts[i]; b = pts[(i+1)%len(pts)]
            n.x += (a.y-b.y)*(a.z+b.z); n.y += (a.z-b.z)*(a.x+b.x); n.z += (a.x-b.x)*(a.y+b.y)
        return n
    rows=[]
    for p in me.polygons:
        vs = list(p.vertices)
        if not any(v in bk for v in vs): continue
        cur = [me.vertices[v].co for v in vs]
        old = [bk.get(v, me.vertices[v].co) for v in vs]
        na, nb = newell(cur), newell(old)
        la, lb = na.length, nb.length
        if la < 1e-12 or lb < 1e-12:
            rows.append((999.0, p.index, la*0.5, p.center.copy())); continue
        d = max(-1.0,min(1.0, na.normalized().dot(nb.normalized())))
        rows.append((math.degrees(math.acos(d)), p.index, la*0.5, p.center.copy()))
    rows.sort(reverse=True)
    print("touched faces: %d" % len(rows))
    areas = sorted(r[2] for r in rows)
    print("face area (local^2): median %.5f  p05 %.6f" % (areas[len(areas)//2], areas[int(.05*len(areas))]))
    print("worst 15 by normal rotation:")
    for ang, idx, area, c in rows[:15]:
        wp = mw @ c
        co = world_to_camera_view(sc, cam, wp)
        print("   %7.2f deg  face %6d  area %.7f  world(%.4f,%.4f,%.4f)  px(%.0f,%.0f) z=%.2f" % (
            ang, idx, area, wp.x,wp.y,wp.z, co.x*1920, (1-co.y)*1080, co.z))
    big = [r for r in rows if r[0] > 5.0]
    print("faces > 5 deg: %d ; their area median %.7f (vs mesh median %.5f)" % (
        len(big), sorted(r[2] for r in big)[len(big)//2] if big else -1, areas[len(areas)//2]))
    bigz = [ (mw @ r[3]).z for r in big ]
    print("their world Z range: %.4f .. %.4f" % (min(bigz), max(bigz)))
finally:
    win.scene=prev
