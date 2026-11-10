from pathlib import Path
import sys
R=Path(__file__).resolve().parent
base=R.parent/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path.insert(0,str(base/'Tools'))
from low_impact import limit_worker
limit_worker(2)
import native_blender as nb
import bpy
from mathutils import Vector
nb.GD=R/'Build/GameData/RoosterWorksStationSupport'
scene=bpy.context.scene
from math import pi
for key,choice,offset,rotation in [('RWG_Hub_250','RWJ_Mixed',0,(0,0,0)),('RWG_Reducer_250_375','RWJ_Core',2.245,(pi,0,pi/4))]:
    old=set(scene.objects);nb.import_model(nb.GD/'Models'/(key+'.mu'),scene)
    for obj in set(scene.objects)-old:
        if obj.parent is None:obj.location=(0,0,offset);obj.rotation_euler=rotation
        parent=obj
        while parent:
            name=parent.name.split('.')[0]
            if name in {'ArmorPanels','ArmorPanelsGrey','RWG_Tank','RWG_Battery','RWG_Xenon','RWJ_Core','RWJ_Mixed'} and name!=choice:obj.hide_render=True
            parent=parent.parent
def place(obj,pos):
    scene.collection.objects.link(obj);obj.location=pos
    obj.rotation_euler=(Vector((0,0,.82))-obj.location).to_track_quat('-Z','Y').to_euler()
for pos,power in [((3,-6,8),2400),((-6,-4,4),1500),((1,4,5),1700)]:
    light=bpy.data.lights.new('Area','AREA');light.energy=power;light.size=7
    place(bpy.data.objects.new('Light',light),pos)
cam=bpy.data.cameras.new('Review');scene.camera=bpy.data.objects.new('Camera',cam)
place(scene.camera,(3,-17,7));cam.type='ORTHO';cam.ortho_scale=5.6
scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.21,.23,.25)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=750;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.filepath=str(R/'Joint-Preview.png');bpy.ops.render.render(write_still=True)
