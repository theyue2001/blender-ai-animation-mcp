import bpy
a=bpy.data.actions.get("P07_SHOT_CAMAction.001")
if a:
    print("orphan: users=%d fake=%s"%(a.users,a.use_fake_user))
    a.use_fake_user=False
    try:
        bpy.data.actions.remove(a, do_unlink=True)
        print("removed P07_SHOT_CAMAction.001")
    except Exception as e:
        print("could not remove:",e)
else:
    print("orphan already gone")
print("P07 actions now:",[x.name for x in bpy.data.actions if x.name.startswith("P07_")])
bpy.ops.wm.save_mainfile()
print("saved to:",bpy.data.filepath)
