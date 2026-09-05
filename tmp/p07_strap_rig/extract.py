import bpy, sys, os
argv = sys.argv[sys.argv.index("--") + 1:]
src, outdir, count = argv[0], argv[1], int(argv[2])
os.makedirs(outdir, exist_ok=True)

clip = bpy.data.movieclips.load(src)
W, H = clip.size[0], clip.size[1]
N = clip.frame_duration
print("CLIP %s  %dx%d  %d frames" % (os.path.basename(src), W, H, N))

scn = bpy.data.scenes.new("EXT")
bpy.context.window.scene = scn
se = scn.sequence_editor_create()
strip = se.sequences.new_movie("m", src, 1, 1)
scale = 1.0
while max(W, H) * scale > 900:
    scale *= 0.5
scn.render.resolution_x = int(W * scale)
scn.render.resolution_y = int(H * scale)
scn.render.resolution_percentage = 100
scn.render.image_settings.file_format = 'PNG'
scn.render.film_transparent = False
scn.view_settings.view_transform = 'Standard'
scn.frame_start = 1
scn.frame_end = N

for i in range(count):
    f = 1 + int((N - 1) * i / max(1, count - 1))
    scn.frame_set(f)
    scn.render.filepath = os.path.join(outdir, "f%03d_%05d.png" % (i, f))
    bpy.ops.render.render(write_still=True)
print("EXTRACTED %d frames of %d to %s" % (count, N, outdir))
