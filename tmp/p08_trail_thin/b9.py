import bpy, json
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
cy=sc.cycles
before={"transparent_max_bounces":cy.transparent_max_bounces,"max_bounces":cy.max_bounces,
        "transmission_bounces":cy.transmission_bounces,"samples":cy.samples}
cy.transparent_max_bounces=64
after={"transparent_max_bounces":cy.transparent_max_bounces}
bpy.ops.wm.save_mainfile()
print(json.dumps({"before":before,"after":after,"saved":True},indent=1))
