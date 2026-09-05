import bpy, json
from mathutils import Vector, Matrix
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
cam = SC.camera; lens=cam.data.lens; sw=cam.data.sensor_width
DEPTH, PLANE_CX = 9.3, 1.6
WIPE, SOFT = -0.26, 0.06        # transparent <=34% of width, opaque >=40%
SHIFT = cam.data.shift_x
gob = bpy.data.objects["P05_GOBO_RIGHT"]
gob.matrix_basis = Matrix.Translation(Vector((PLANE_CX, 0.0, -DEPTH)))
half_w = 0.5*sw*DEPTH/lens
centre = SHIFT*sw*DEPTH/lens
wipe_x = centre + WIPE*half_w
soft   = SOFT*half_w
mr = bpy.data.materials["MAT_P05_GOBO"].node_tree.nodes["EDGE"]
lo, hi = (wipe_x-PLANE_CX)-soft, (wipe_x-PLANE_CX)+soft
mr.inputs[1].default_value = lo
mr.inputs[2].default_value = hi
bpy.ops.wm.save_mainfile()
print(json.dumps({"shift":round(SHIFT,4), "wipe_cam_x":round(wipe_x,3),
                  "ramp_local":[round(lo,3),round(hi,3)], "plane_local_x":[-4+PLANE_CX, 4+PLANE_CX],
                  "wipe_pct_of_width":[round(100*(0.5-SHIFT+(WIPE-SOFT)*0.5),1), round(100*(0.5-SHIFT+(WIPE+SOFT)*0.5),1)]}))
bpy.context.window.scene = prev
