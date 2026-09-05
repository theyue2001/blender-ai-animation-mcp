import bpy, json, math
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
out={"range":[sc.frame_start,sc.frame_end],"engine":sc.render.engine,
     "view":{"vt":sc.view_settings.view_transform,"look":sc.view_settings.look,
             "exposure":round(sc.view_settings.exposure,3)},
     "world":sc.world.name if sc.world else None}
mk=sorted([(m.frame,m.name,m.camera.name if m.camera else None) for m in sc.timeline_markers])
out["shots"]=mk
# world background
if sc.world and sc.world.use_nodes:
    for n in sc.world.node_tree.nodes:
        if n.type=='BACKGROUND':
            out["world_bg"]={"color":[round(v,3) for v in n.inputs[0].default_value],
                             "strength":round(n.inputs[1].default_value,3)}
def visible(o,f):
    ad=o.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            if fc.data_path=="hide_render": return fc.evaluate(f)<0.5
    return not o.hide_render
# per-shot: which meshes/lights are visible at the shot midpoint
bounds=[(mk[i][0], mk[i+1][0]-1 if i+1<len(mk) else sc.frame_end) for i in range(len(mk))]
for (start,end),(_,name,cam) in zip(bounds,mk):
    mid=(start+end)//2
    vis_m=[o.name for o in sc.objects if o.type=='MESH' and visible(o,mid)]
    vis_l=[(o.name,round(o.data.energy,1)) for o in sc.objects if o.type=='LIGHT' and visible(o,mid)]
    c=bpy.data.objects.get(cam) if cam else None
    out.setdefault("detail",{})[name]={
        "frames":[start,end],"len_s":round((end-start+1)/24.0,2),"cam":cam,
        "cam_lens":round(c.data.lens,1) if c else None,
        "cam_loc":[round(v,2) for v in c.matrix_world.translation] if c else None,
        "n_visible_meshes":len(vis_m),
        "visible_meshes":vis_m[:14],
        "visible_lights":vis_l[:10]}
print(json.dumps(out,indent=1,ensure_ascii=False))
