import bpy
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
print("world:", sc.world.name if sc.world else None, "users:", sc.world.users if sc.world else 0)
if sc.world:
    print("  used by scenes:", [s.name for s in bpy.data.scenes if s.world==sc.world])
    nt=sc.world.node_tree
    if nt:
        for n in nt.nodes:
            if n.type in ('BACKGROUND','TEX_ENVIRONMENT','RGB'):
                vals=[]
                for i in n.inputs:
                    try: vals.append("%s=%s"%(i.name, tuple(round(v,3) for v in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)))
                    except Exception: pass
                print("  node %-16s %-18s %s"%(n.name,n.type," ".join(vals)))
print("view_transform:", sc.view_settings.view_transform, "look:", sc.view_settings.look, "exposure:", round(sc.view_settings.exposure,3))
print("engine:", sc.render.engine)
for o in sc.objects:
    if o.type=='LIGHT':
        d=o.data
        print("light %-12s %-6s energy=%.1f size=%s color=%s loc=%s"%(o.name,d.type,d.energy,
              getattr(d,'size',None),tuple(round(v,2) for v in d.color),tuple(round(v,2) for v in o.location)))
