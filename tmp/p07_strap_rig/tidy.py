import bpy
n=0
for a in list(bpy.data.actions):
    if a.name=="P07_SHOT_CAMAction.001" and a.users==0:
        a.use_fake_user=False; bpy.data.actions.remove(a); n+=1
print("removed %d orphan action(s); actions now: %s"%(n,[a.name for a in bpy.data.actions if a.name.startswith("P07_")]))
bpy.ops.wm.save_mainfile(); print("saved")
