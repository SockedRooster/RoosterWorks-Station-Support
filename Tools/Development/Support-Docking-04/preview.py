from pathlib import Path
import sys
R=Path(__file__).resolve().parent
base=R.parent/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path.insert(0,str(base/'Tools'))
from low_impact import limit_worker
limit_worker(2)
import native_blender as nb
import bpy
nb.GD=R.parent/'Support-Joints-02/Build/GameData/RoosterWorksStationSupport'
scene=bpy.context.scene
choices=[('RWG_Docking_125','',-2.8,0),('RWG_Docking_250','ArmorPanels',-.65,0),('RWG_Docking_375','ArmorPanelsGrey',2.8,0)]
for key,choice,x,z in choices:
    old=set(scene.objects);nb.import_model(R/'Build'/(key+'.mu'),scene)
    for obj in set(scene.objects)-old:
        if obj.parent is None:obj.location=(x,0,z)
        parent=obj
        while parent:
            name=parent.name.split('.')[0]
            if name in ('ArmorPanels','ArmorPanelsGrey','RWG_Tank','RWG_Battery','RWG_Xenon') and name!=choice:obj.hide_render=True
            parent=parent.parent
def place(obj,pos):
    scene.collection.objects.link(obj);obj.location=pos
    obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
for pos,power in [((3,-6,8),2400),((-6,-4,4),1500),((1,4,5),1700)]:
    light=bpy.data.lights.new('Area','AREA');light.energy=power;light.size=7
    place(bpy.data.objects.new('Light',light),pos)
cam=bpy.data.cameras.new('Review');scene.camera=bpy.data.objects.new('Camera',cam)
place(scene.camera,(1,-12,9));cam.type='ORTHO';cam.ortho_scale=9.8
scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.21,.23,.25)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1000;scene.render.resolution_y=350;scene.render.resolution_percentage=100
scene.render.filepath=str(R/'Couplers.png');bpy.ops.render.render(write_still=True)
