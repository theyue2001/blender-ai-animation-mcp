# Project Instructions

## Blender Animation Progress Tracking

Whenever working on Blender animation tasks in this project, always create and maintain a visible progress checklist **before** starting the actual modifications.

### Rules

1. Before making changes, break the task into clear execution steps.
2. Display these steps using Claude Code's Todo/Task progress system.
3. Update the checklist continuously while working — not only after everything is finished.
4. Mark each item as one of:
   - **Pending**
   - **In Progress**
   - **Completed**
   - **Blocked/Failed**
5. Only mark a task **Completed** after it has actually been executed and verified.
6. Never claim progress based only on planned work.
7. If a step fails, show it as **Blocked/Failed** and explain the reason before retrying.
8. Keep the progress list visible and update it after each major Blender/MCP operation.
9. Do not stop to ask for confirmation between normal steps unless the action is destructive or fundamentally changes the requested design.
10. Continue using the CURRENT `.blend` file and persist changes with a normal Save. Do not create repeated "Save As" versions for routine work.
    - **Exception (version checkpoint):** once an accumulated batch exceeds **5 new animations** or **10 modifications**, a "Save As" checkpoint is allowed.
    - Count new animations and modifications since the last checkpoint; either threshold on its own is enough to trigger it.
    - When creating a checkpoint: state that the threshold was reached, keep working in the newly saved file afterwards, and use an incrementing version suffix (e.g. `..._v031.blend` → `..._v032.blend`) instead of ad-hoc names like `_final` / `_backup`.
    - Below those thresholds, still save in place — do not create a checkpoint per step.
11. Do not use fake or estimated completion percentages. Report only real, verified step state.
12. Progress must be visible **while working**, not summarized only in the final response.

### Scope

These rules apply to **all Blender MCP animation work in this project**, including keyframing,
F-curve edits, camera/lighting/material animation, shape keys, drivers, NLA work, preview
renders, and animation export passes.

### Standard Progress Structure

For Blender animation work, normally structure progress approximately like this:

```
[ ] Inspect current Blender scene and animation state
[ ] Inspect objects, hierarchy, cameras, lights, materials and timeline
[ ] Determine the animation changes required
[ ] Create/modify object animation
[ ] Create/modify camera animation
[ ] Create/modify lighting/material/emission animation
[ ] Check keyframes, F-curves and interpolation
[ ] Generate preview/check frames
[ ] Visually inspect animation quality
[ ] Fix detected animation or rendering issues
[ ] Final verification
[ ] Save the CURRENT Blender file
```

When working on only part of an animation, adapt the checklist to the actual task instead of
blindly using every step.

**IMPORTANT:** Keep updating the Todo/Progress state during execution so the current activity and
the remaining work are immediately visible.
