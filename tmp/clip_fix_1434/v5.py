import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=[]
win=bpy.context.window; prev=win.scene
m011 = bpy.data.meshes["mesh.011"]; m045 = bpy.data.meshes["mesh.045"]
out.append("mesh.011 users=%d objects=%s" % (m011.users,[o.name for o in bpy.data.objects if o.data is m011]))
out.append("mesh.045 users=%d objects=%s" % (m045.users,[o.name for o in bpy.data.objects if o.data is m045]))
m2 = bpy.data.meshes.get("mesh.011_P05_ARMGAP")
out.append("mesh.011_P05_ARMGAP users=%d objects=%s" % (m2.users,[o.name for o in bpy.data.objects if o.data is m2]))
for o in bpy.data.objects:
    if o.data is m011:
        scns=[s.name for s in bpy.data.scenes if o.name in s.objects]
        out.append("   %-24s in scenes %s" % (o.name, scns))
# prove the ORIGINAL pair is still coincident (i.e. untouched) using raw mesh data
try:
    a = next(o for o in bpy.data.objects if o.data is m011 and o.name != "X5_16_0.002")
    b = next(o for o in bpy.data.objects if o.data is m045 and o.name != "X5_61.002")
    def tr(o):
        bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
        bmesh.ops.triangulate(bm,faces=bm.faces); t=BVHTree.FromBMesh(bm); bm.free(); return t
    out.append("ORIGINAL %s x %s overlap = %d tris (baseline 1705 => untouched)" % (a.name,b.name,len(tr(a).overlap(tr(b)))))
except StopIteration:
    out.append("could not find original pair")
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
try:
    win.scene = sc; sc.frame_set(1434)
    ob = sc.objects["X5_16_0.002"]; me = ob.data
    out.append("P05 cover: mesh=%s verts=%d polys=%d custom_normals=%s slots=%s" % (
        me.name, len(me.vertices), len(me.polygons), me.has_custom_normals,
        [(s.link, s.material.name if s.material else None) for s in ob.material_slots]))
    bm=bmesh.new(); bm.from_mesh(me)
    out.append("degenerate faces=%d  loose verts=%d  smooth polys=%d/%d" % (
        sum(1 for f in bm.faces if f.calc_area()<=0.0), sum(1 for v in bm.verts if not v.link_faces),
        sum(1 for p in me.polygons if p.use_smooth), len(me.polygons)))
    bm.free()
    out.append("scene.camera=%s markers=%s" % (sc.camera.name,
               [(m.frame, m.camera.name if m.camera else None) for m in sc.timeline_markers]))
    out.append("engine=%s res=%dx%d %d%% samples=%d out=%s" % (sc.render.engine, sc.render.resolution_x,
               sc.render.resolution_y, sc.render.resolution_percentage, sc.cycles.samples, sc.render.filepath))
finally:
    win.scene=prev
out.append("window scene: %s frame %d" % (bpy.context.window.scene.name, bpy.context.window.scene.frame_current))
print("\n".join(out))
