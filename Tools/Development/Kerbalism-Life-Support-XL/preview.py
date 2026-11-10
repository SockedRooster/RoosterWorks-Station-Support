from pathlib import Path
import sys
here=Path(__file__).resolve().parent
base=here.parent/'Releases/2026-11-02/RoosterWorks-Station-Support-v1.0.9-Source'
sys.path.insert(0,str(base/'Tools'))
from low_impact import limit_worker
limit_worker(2)
import native_blender as nb
import bpy
from mathutils import Vector
scene=bpy.context.scene
nb.import_model(base/'GameData/RoosterWorksStationSupport/Models/RW_OctoSupport_XL.mu',scene)
hidden={'RWSS_Battery','RWSS_Standard','RWSS_ServiceCore','RWSS_TankPack','RWSS_XenonPack','ArmorPanels','ArmorPanelsGrey'}
for obj in scene.objects:
    parent=obj
    while parent:
        if parent.name.split('.')[0] in hidden:obj.hide_render=True
        parent=parent.parent
nb.GD=here/'GameData/RoosterWorksKerbalismSupport'
nb.import_model(nb.GD/'Models/RWSS_KLS_XL.mu',scene)
def place(obj,pos):
    scene.collection.objects.link(obj);obj.location=pos
    obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
for pos,power,size in [((4,6,7),1400,5),((-3,4,2),900,4),((0,-4,5),1100,4)]:
    light=bpy.data.lights.new('Softbox','AREA');light.energy=power;light.size=size
    place(bpy.data.objects.new('Light',light),pos)
cam=bpy.data.cameras.new('Review');scene.camera=bpy.data.objects.new('Camera',cam)
place(scene.camera,(2.5,9,3));cam.type='ORTHO';cam.ortho_scale=5.7
scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.20,.23,.26)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.filepath=str(here/'Octo-XL-Life-Support.png')
bpy.ops.render.render(write_still=True)
