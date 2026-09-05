import bpy, json
out={}
for s in bpy.data.scenes:
    fps = s.render.fps / s.render.fps_base
    n = s.frame_end - s.frame_start + 1
    out[s.name] = {"fps": fps, "fps_base": round(s.render.fps_base,4), "range":[s.frame_start,s.frame_end],
                   "frames": n, "sec_at_this_fps": round(n/fps,2), "sec_at_30": round(n/30.0,2),
                   "start_at_30": round(s.frame_start/30.0,2), "end_at_30": round(s.frame_end/30.0,2)}
print(json.dumps(out, ensure_ascii=False, indent=1))
