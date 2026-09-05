import bpy, json
log={}
for n in ["LGT_Opening_Logo_Highlight","LGT_Opening_Logo_Accent","LGT_Opening_Silhouette_Rim_L","LGT_Opening_Silhouette_Top"]:
    o=bpy.data.objects.get(n)
    if o: log[n]={"cam":o.visible_camera,"diff":o.visible_diffuse,"glossy":o.visible_glossy}
lo=bpy.data.objects["LGT_Opening_Logo_Highlight"]
lo.visible_camera=False
log["after"]={"cam":lo.visible_camera}
bpy.ops.wm.save_mainfile()
print(json.dumps(log, indent=1))
