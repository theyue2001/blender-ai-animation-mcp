import bpy, json
KNOWN = {"INST_Opening_NITE_Product","INST_Opening_Human","CTRL_Opening_Black_Target",
"CTRL_Opening_Silhouette_Target","CTRL_Opening_Worn_Target","CAM_Opening_Black",
"CAM_Opening_Silhouette","CAM_Opening_Worn","LGT_Opening_Silhouette_Rim_L",
"LGT_Opening_Silhouette_Rim_R","LGT_Opening_Silhouette_Top","LGT_Opening_Logo_Accent",
"LGT_Opening_Worn_Rim_L","LGT_Opening_Worn_Rim_R","LGT_Opening_Worn_Key",
"LGT_Opening_Worn_Product_Fill"}
sc1 = bpy.data.scenes["01_SCN_OPENING_P01_P03"]
cur = {o.name for o in sc1.objects}
new = sorted(cur - KNOWN)
out = {"n": len(cur), "new": new, "missing": sorted(KNOWN - cur)}
out["colls_of_scene1"] = [c.name for c in sc1.collection.children_recursive]
out["direct"] = [o.name for o in sc1.collection.objects]
for n in new:
    o = bpy.data.objects[n]
    out["info_"+n] = {"type":o.type, "colls":[c.name for c in o.users_collection],
                      "scenes":[s.name for s in bpy.data.scenes if o.name in s.objects]}
print(json.dumps(out, ensure_ascii=False, indent=1))
