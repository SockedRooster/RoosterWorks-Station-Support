# v1.0.5 verification

Compared with the v1.0.4 player ZIP, only three adapter configs, two shared adapter MU files and version metadata changed. Every other game file is identical, including all girders, textures, capacities, prices and the extra-selector compatibility patch.

The white shell mesh is duplicated as Body_grey_00 with the RW_steel material used by grey girder armor. Vertices, UVs, normals and triangles are identical between shell colors. Existing meshes, transforms and collision shapes are preserved. White is enabled by default; each variant disables the opposite shell. Both variants have zero mass/cost deltas. The 3.75 m adapter continues sharing the scaled Octo 2.5 m model.

User-confirmed in-game for v1.0.4: redundant selector removed and new 3.75 m capacities correct.
Pending for v1.0.5: adapter finish switching and persistence in KSP. Blender preview is an approximation of materials, not a KSP screenshot.
