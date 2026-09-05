import bpy, json, colorsys
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
SHIFT = 14.0/360.0
def rot(sock):
    r,g,b,a = sock.default_value
    h,s,v = colorsys.rgb_to_hsv(r,g,b)
    nr,ng,nb = colorsys.hsv_to_rgb((h+SHIFT)%1.0, s, v)
    sock.default_value = (nr,ng,nb,a)
    return [round(h*360,1), round(((h+SHIFT)%1.0)*360,1), [round(nr,3),round(ng,3),round(nb,3)]]
rep={}
nt = bpy.data.materials["MAT_P05_Silicone_White"].node_tree
rep["sleeve_base"] = rot(nt.nodes["SILICONE"].inputs["Base Color"])
rep["sleeve_emis"] = rot(nt.nodes["SILICONE"].inputs["Emission Color"])
rep["sleeve_milk"] = rot(nt.nodes["MILK"].inputs["Color"])
nt2 = bpy.data.materials["MAT_P05_Cartridge_Amber"].node_tree
rep["cart_base"]  = rot(nt2.nodes["AMB_SURF"].inputs["Base Color"])
rep["cart_emis"]  = rot(nt2.nodes["AMB_SURF"].inputs["Emission Color"])
rep["cart_clear"] = rot(nt2.nodes["AMB_CLEAR"].inputs["Color"])
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
