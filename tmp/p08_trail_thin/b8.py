import bpy, json
rep={}
for k in "ABC":
    nt=bpy.data.materials["MAT_P08_CMPSEC_%s"%k].node_tree
    if "CUT_FLIP" in nt.nodes:
        nt.nodes.remove(nt.nodes["CUT_FLIP"])
        rep["MAT_P08_CMPSEC_%s"%k]="CUT_FLIP removed (Cycles already flips backface shading normals)"
    face=nt.nodes["CUT_FACE"]
    rep.setdefault("normal_linked",{})[k]=face.inputs["Normal"].is_linked
bpy.ops.wm.save_mainfile()
rep["saved"]=True
print(json.dumps(rep,indent=1))
