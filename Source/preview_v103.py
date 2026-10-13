"""Render three finishes on scaled 3.75 m hollow girders in Blender: blender -b --python Source/preview_hollow.py.

Preview uses palette colors and Blender lighting, not KSP's shader or game engine.
"""
from pathlib import Path
import sys, math
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Source'))
from read_mu import Reader

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.world.color=(.22,.22,.22)
scene.view_settings.view_transform='AgX'
colors=[(112,125,137),(37,52,65),(202,211,209),(174,121,64),(181,193,195),(25,42,56),(54,255,92),(244,246,242)]
mats=[]
for i,color in enumerate(colors):
    m=bpy.data.materials.new(f'RW_{i}')
    m.diffuse_color=tuple((x/255)**2.2 for x in color)+(1,)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=m.diffuse_color
    bs.inputs['Metallic'].default_value=.35
    bs.inputs['Roughness'].default_value=.42
    mats.append(m)
for part,offset,finish in [('RW_OctoSupport_Medium_Hollow',-4.5,'Open'),('RW_OctoSupport_Medium_Hollow',0,'ArmorPanels'),('RW_OctoSupport_Medium_Hollow',4.5,'ArmorPanelsGrey')]:
    model=Reader(ROOT/'GameData/RoosterWorksStationSupport/Models'/f'{part}.mu')
    for i,m in enumerate(model.meshes):
        group=m['node']['parent']['name']
        if model.armored(m) and group!=finish: continue
        mesh=bpy.data.meshes.new(f'{part}_{i}')
        mesh.from_pydata([(-x*1.5+offset,-z*1.5,y*1.5+2.1) for x,y,z in m['verts']],[],[(a,c,b) for a,b,c in m['tris']])
        mesh.update()
        obj=bpy.data.objects.new(mesh.name,mesh)
        bpy.context.collection.objects.link(obj)
        mesh.materials.append(mats[m['material']])
        for face in mesh.polygons: face.use_smooth=True
        mesh.normals_split_custom_set_from_vertices([(-x,-z,y) for x,y,z in m['normals']])
bpy.ops.mesh.primitive_plane_add(size=200)
floor=bpy.context.object
floor.location.z=-.05
mat=bpy.data.materials.new('Ground')
mat.diffuse_color=(.08,.09,.11,1)
floor.data.materials.append(mat)
for loc,power,size in [((1,-7,11),2100,7),((-6,0,7),1300,6),((4,5,9),2200,5)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    light=bpy.context.object
    light.data.energy=power
    light.data.shape='DISK'
    light.data.size=size
    light.rotation_euler=(Vector((0,0,2))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-5,-18,11))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,2.3))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'
cam.data.ortho_scale=17
scene.camera=cam
out=ROOT/'Previews'
out.mkdir(exist_ok=True)
scene.render.filepath=str(out/'v103-three-finishes.png')
bpy.ops.render.render(write_still=True)
