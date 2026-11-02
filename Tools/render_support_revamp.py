"""Review exact MU output with all major resource and appearance combinations."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'Tools'),str(R/'.build-deps')]
from low_impact import limit_worker
limit_worker(2)
import native_blender as nb
import bpy,math,numpy as np
from PIL import Image,ImageDraw,ImageFont
from mathutils import Vector
OUT=R/'Previews/SupportWiring04';OUT.mkdir(exist_ok=True)
M=R/'GameData/RoosterWorksStationSupport/Models'
for kind in ('metal','insulation'):
    packed=np.asarray(Image.open(M/f'rwss_{kind}_NRM.dds').convert('RGBA'),dtype=float)[::-1]/255
    x=packed[:,:,3]*2-1;y=packed[:,:,1]*2-1;z=np.sqrt(np.maximum(0,1-x*x-y*y));Image.fromarray(np.uint8(np.stack((x,y,z),axis=-1)*127.5+127.5)).save(OUT/f'{kind}_normal.png')
def material(src,model):
    name=src['name']
    if name in nb.materials:return nb.materials[name]
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
    texture=model.textures[src['properties']['_MainTex']['index']]['name'];tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(M/(texture+'.png')),check_existing=True);tex.image.alpha_mode='CHANNEL_PACKED';tex.image.pack();links.new(tex.outputs['Color'],p.inputs['Base Color'])
    p.inputs['Metallic'].default_value=.65 if name.endswith(('steel','tank','bronze')) else .12;p.inputs['Roughness'].default_value=.40 if name.endswith(('steel','tank','bronze')) else .57
    if '_BumpMap' in src['properties']:
        kind='insulation' if 'insulation' in name else 'metal';tn=nodes.new('ShaderNodeTexImage');tn.image=bpy.data.images.load(str(OUT/f'{kind}_normal.png'),check_existing=True);tn.image.colorspace_settings.name='Non-Color';tn.image.pack();normal=nodes.new('ShaderNodeNormalMap');links.new(tn.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],p.inputs['Normal'])
    nb.materials[name]=mat;return mat
nb.material=material
def aim(obj,p):obj.rotation_euler=(Vector(p)-obj.location).to_track_quat('-Z','Y').to_euler()
def add(scene,key,interior='RWSS_Standard',armor=None,offset=(0,0,0),scale=1,baseline=False):
    old=set(scene.objects);nb.import_model((R/'Source/RevampBaseline/GameData/RoosterWorksStationSupport/Models' if baseline else M)/(key+'.mu'),scene)
    for obj in set(scene.objects)-old:
        if obj.parent is None:obj.location=offset;obj.scale=(scale,scale,scale)
        p=obj
        while p:
            name=p.name.split('.')[0]
            if name in ('RWSS_Standard','RWSS_Battery','RWSS_TankPack','RWSS_XenonPack','RWSS_ServiceCore') and name!=interior:obj.hide_render=True
            if name in ('ArmorPanels','ArmorPanelsGrey','Body_white_00','Body_grey_00') and name!=(armor or ('Body_white_00' if 'Adapter' in key else '')):obj.hide_render=True
            p=p.parent
shots=[('Family','RW_OctoSupport_Medium','RWSS_TankPack',None)]
for shot,key,interior,armor in shots:
    nb.materials={};scene=bpy.data.scenes.new(shot);bpy.context.window.scene=scene
    if shot=='Family':
        add(scene,'RW_OctoSupport_Medium','RWSS_TankPack');add(scene,'RW_OctoSupport_Medium','RWSS_ServiceCore',offset=(0,0,2.65));span=3.2;target=(0,0,1.6);pos=(7,-5,4)
    else:
        add(scene,key,interior,armor,baseline=shot=='Before');span=5.9 if 'XL' in key else (4 if 'Hex' not in key else 4.0);target=(0,0,0);pos=(6,10,5)
        if shot=='Adapter':span=3.6
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.render.threads_mode='FIXED';scene.render.threads=2;scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
    world=bpy.data.worlds.new(shot);scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.065,.083,.10,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    for loc,power,size in [((4,7,8),2000,6),((-6,3,6),1500,5),((0,-6,3),1800,5)]:
        data=bpy.data.lights.new('Studio','AREA');obj=bpy.data.objects.new('Studio',data);scene.collection.objects.link(obj);obj.location=loc;data.energy=power;data.size=size;aim(obj,target)
    data=bpy.data.cameras.new(shot);obj=bpy.data.objects.new(shot,data);scene.collection.objects.link(obj);scene.camera=obj;obj.location=pos;data.type='ORTHO';data.ortho_scale=span;aim(obj,target)
    scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(shot+'.png'));bpy.ops.render.render(write_still=True);print('Rendered',shot,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Source/Blender/RW_SupportWiring04.blend'))
sheet=Image.new('RGB',(1800,580),(16,23,29));d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',28)
for j,name in enumerate(('Family',)):
    im=Image.open(OUT/(name+'.png')).convert('RGB');im.thumbnail((560,520));x=j%4*600;y=j//4*580;sheet.paste(im,(x+20,y+50));d.text((x+25,y+12),name.upper(),font=font,fill=(226,218,195))
sheet.save(OUT/'Review.png')
