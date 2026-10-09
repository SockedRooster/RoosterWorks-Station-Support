"""RoosterWorks Station Support — procedural Blender model generator.

Blender 4.2+ / 4.5 LTS / Blender 5.x (designed for those versions; runtime testing required).
Open in Blender > Scripting > Open > Run Script. No add-ons required to MODEL.

Creates ONE static model from the PART choice below, including:
  - sealed smooth round truss bars, reinforced joints and rings
  - custom internal monopropellant vessels and full-height battery banks
  - green LED geometry and emissive shader (optional Blender-only flashing)
  - separate Armored Panels parent for eventual KSP PartVariants
  - legible RoosterWorks badge as real 3D text geometry
  - optional lighting/camera preview and .blend output

IMPORTANT: Blender FBX/GLB is NOT a native Kerbal Space Program .mu.
Use a separate Unity + KSP PartTools workflow for final .mu conversion.
Procedural shader noise requires baking to image textures for KSP.
"""

import bpy
import math
from pathlib import Path
from mathutils import Vector, Matrix

# ======================== USER SETTINGS ============================
# Start with OCTO_XL for the quality benchmark, then try the other presets.
PART = "OCTO_XL"  # OCTO_XL, OCTO_MEDIUM, HEX_LONG, HEX_MEDIUM, OCTO_25_ADAPTER, HEX_125_ADAPTER
SHOW_ARMOR = False                  # False: open-frame; True: panel-clad truss
ADD_INNER_OCTAGON_SPOKES = True    # Add structural radial supports to inner octagonal end rings
INNER_SPOKE_RADIUS = 0.033         # Octo XL/Medium spoke radius in meters
ANIMATE_LED_PREVIEW = False         # Blender shader ONLY, not exported as KSP flashing lights
ADD_STUDIO_CAMERA_AND_LIGHTS = True
AUTO_SAVE_BLEND = True
EXPORT_FBX = False                  # Optional intermediate asset; not a .mu file
OUTPUT_DIR = Path.home() / "Documents" / "RoosterWorks_Blender"
# ==================================================================

SPECS = {
    "OCTO_XL": dict(part_id="RW_OctoSupport_XL", sides=8, diameter=2.5, height=4.75,
                    tanks=4, tank_r=.3965625, radius_centers=.565, ec=9000, mono=1500, node=2),
    "OCTO_MEDIUM": dict(part_id="RW_OctoSupport_Medium", sides=8, diameter=2.5, height=2.65,
                        tanks=3, tank_r=.395, radius_centers=.53, ec=4500, mono=750, node=2),
    "HEX_LONG": dict(part_id="RW_HexSupport_Long", sides=6, diameter=1.25, height=3.15,
                     tanks=4, tank_r=.19828125, radius_centers=.202, ec=1200, mono=200, node=1),
    "HEX_MEDIUM": dict(part_id="RW_HexSupport_Medium", sides=6, diameter=1.25, height=1.75,
                       tanks=1, tank_r=.370125, radius_centers=0, ec=600, mono=100, node=1),
    "OCTO_25_ADAPTER": dict(part_id="RW_Octo25_Adapter", sides=8, diameter=2.5,
                            height=.74, node=2, ec=0, mono=0),
    "HEX_125_ADAPTER": dict(part_id="RW_Hex125_Adapter", sides=6, diameter=1.25,
                            height=.56, node=1, ec=0, mono=0),
}
if PART not in SPECS:
    raise ValueError(f"Invalid PART={PART}. Choose one of: {', '.join(SPECS)}")

SPEC = SPECS[PART]
PART_ID = SPEC['part_id']
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def reset_scene():
    if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.users == 0:
            bpy.data.collections.remove(collection)


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def move_to_collection(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def parent_and_group(obj, owner, coll):
    move_to_collection(obj, coll)
    obj.parent = owner
    return obj


def new_empty(name, owner=None, group=None):
    obj = bpy.data.objects.new(name, None)
    (group or MODEL_COLL).objects.link(obj)
    obj.empty_display_type = 'PLAIN_AXES'
    obj.empty_display_size = .12
    if owner:
        obj.parent = owner
    return obj


def pbr(name, color, metallic=0.0, roughness=.5, noise=.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (350, 70)
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    shader.location = (100, 70)
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    mat.node_tree.links.new(shader.outputs['BSDF'], out.inputs['Surface'])
    if noise:
        tex = nodes.new('ShaderNodeTexNoise')
        tex.location = (-380, -120)
        tex.inputs['Scale'].default_value = 125.0
        tex.inputs['Detail'].default_value = 2.0
        bump = nodes.new('ShaderNodeBump')
        bump.location = (-130, -100)
        bump.inputs['Strength'].default_value = noise
        bump.inputs['Distance'].default_value = .004
        mat.node_tree.links.new(tex.outputs['Fac'], bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'], shader.inputs['Normal'])
    return mat


reset_scene()
MODEL_COLL = collection('RW_MODEL_BASE')
ARMOR_COLL = collection('RW_OPTIONAL_ARMOR')
GUIDES_COLL = collection('RW_KSP_EXPORT_GUIDES_DO_NOT_RENDER')
PREVIEW_COLL = collection('RW_PREVIEW_LIGHTS_CAMERA_DO_NOT_EXPORT')
ROOT = new_empty(PART_ID, group=MODEL_COLL)
ARMOR_ROOT = new_empty('ArmorPanels', owner=ROOT, group=ARMOR_COLL)

steel = pbr('RW_01_Painted_Solid_Steel', (.30, .35, .40), metallic=.78, roughness=.29, noise=.055)
steel_dark = pbr('RW_02_Dark_Frame', (.09, .13, .17), metallic=.72, roughness=.36, noise=.045)
white = pbr('RW_03_Ceramic_White', (.79, .82, .81), metallic=.24, roughness=.38, noise=.065)
bronze = pbr('RW_04_Anodized_Gold', (.53, .31, .11), metallic=.80, roughness=.31, noise=.055)
tank_metal = pbr('RW_05_Brushed_Titanium_Tank', (.70, .75, .76), metallic=.72, roughness=.29, noise=.05)
battery_mat = pbr('RW_06_Power_Bank_Dark', (.065, .10, .14), metallic=.42, roughness=.43, noise=.045)
glass = pbr('RW_07_Black_Insulator', (.017, .035, .043), metallic=.16, roughness=.29)
white_text = pbr('RW_08_White_Label', (.93, .94, .91), metallic=.05, roughness=.42)

led_green = bpy.data.materials.new('RW_09_LED_Green_Emissive')
led_green.use_nodes = True
led_green.diffuse_color = (.08, 1.0, .22, 1.0)
led_nodes = led_green.node_tree.nodes
led_bsdf = led_nodes.get('Principled BSDF')
led_bsdf.inputs['Base Color'].default_value = (.05, .85, .12, 1)
led_bsdf.inputs['Roughness'].default_value = .2
if 'Emission Color' in led_bsdf.inputs:
    led_bsdf.inputs['Emission Color'].default_value = (.1, 1, .24, 1)
if 'Emission Strength' in led_bsdf.inputs:
    led_bsdf.inputs['Emission Strength'].default_value = 3.0
    if ANIMATE_LED_PREVIEW:
        for frame in range(1, 145, 24):
            for offset, strength in ((0, .15), (6, 3.2), (13, 3.2), (18, .15), (23, .15)):
                inp = led_bsdf.inputs['Emission Strength']
                inp.default_value = strength
                inp.keyframe_insert(data_path='default_value', frame=frame+offset)
        led_bsdf.inputs['Emission Strength'].default_value = 3.0


def apply_material(obj, material):
    if obj.type == 'MESH':
        obj.data.materials.append(material)
    return obj


def finish_mesh(obj, group, owner, mat, smooth=False):
    parent_and_group(obj, owner, group)
    apply_material(obj, mat)
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def add_bevel(obj, amount=.01, segments=3):
    mod = obj.modifiers.new('Rounded_Edges', 'BEVEL')
    mod.width = amount
    mod.segments = segments
    if hasattr(mod, 'affect'):
        mod.affect = 'EDGES'
    mod.loop_slide = True
    return obj


def box(name, pos, dims, mat, group=MODEL_COLL, owner=ROOT, bevel=.0, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation:
        obj.rotation_euler = rotation.to_euler() if hasattr(rotation, 'to_euler') else rotation
    finish_mesh(obj, group, owner, mat)
    if bevel:
        add_bevel(obj, bevel)
    return obj


def cylinder(name, a, b, radius, mat, vertices=40, group=MODEL_COLL, owner=ROOT, bevel=.006):
    """A genuine, manifold, closed cylinder with caps and outward-facing faces.

    Blender cylinder meshes avoid the inverted winding that produced U-shaped
    rails in the former custom .mu generator.
    """
    p0, p1 = Vector(a), Vector(b)
    direction = p1-p0
    if direction.length < 1e-6:
        raise ValueError('Cylinder endpoints must differ')
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=direction.length,
        end_fill_type='NGON', calc_uvs=True, location=(p0+p1)*.5)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat('Z','Y').to_euler()
    finish_mesh(obj, group, owner, mat)
    # Smooth only side faces; keep end-cap shading flat.
    for poly in obj.data.polygons:
        poly.use_smooth = abs(poly.normal.z) < .45
    if bevel:
        add_bevel(obj, min(bevel, radius*.17), 3)
    return obj


def sphere(name, loc, radius, mat, group=MODEL_COLL, owner=ROOT, seg=16, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=radius, location=loc)
    obj=bpy.context.object
    obj.name=name
    return finish_mesh(obj, group, owner, mat, smooth=True)


def ring_points(count, rad, y):
    return [Vector((rad*math.cos(i*math.tau/count),y,rad*math.sin(i*math.tau/count)))
            for i in range(count)]


def face_coords(n, i, rad):
    # Face normal and camera-facing right vector, with right x up = outward.
    theta=(i+.5)*math.tau/n
    normal=Vector((math.cos(theta),0,math.sin(theta)))
    right=Vector((math.sin(theta),0,-math.cos(theta)))
    up=Vector((0,1,0))
    rot=Matrix((right,up,normal)).transposed().to_quaternion()
    apothem=rad*math.cos(math.pi/n)
    return normal, right, rot, apothem


def badge(name, normal, rot, world_pos, width, height):
    """Actual 3-D text, rather than backwards UV-mapped artwork."""
    box(name+'_Backing', world_pos, (width,height,.020), steel_dark, bevel=.010, rotation=rot)
    # Edge rails emphasize readable exterior badge.
    local_right = rot @ Vector((1,0,0))
    local_up = rot @ Vector((0,1,0))
    for sign in (-1,1):
        center=Vector(world_pos)+local_up*(sign*(height/2-.016))+normal*.016
        cylinder(name+'_Trim', center-local_right*(width*.48), center+local_right*(width*.48),
                 radius=.006,mat=bronze,vertices=12,bevel=.002)
    for message, yoff, font_size, mat in [
            ('RoosterWorks',height*.16,height*.5,white_text),
            ('Station Support',-height*.22,height*.25,bronze)]:
        bpy.ops.object.text_add(location=Vector(world_pos)+normal*.022+local_up*yoff)
        obj=bpy.context.object
        obj.name=name+'_Text_'+message.replace(' ','_')
        obj.rotation_euler=rot.to_euler()
        obj.data.body=message
        obj.data.align_x='CENTER'
        obj.data.align_y='CENTER'
        obj.data.size=font_size
        obj.data.extrude=.00055
        obj.data.bevel_depth=.00018
        obj.data.bevel_resolution=2
        # Convert to editable mesh; font files are never included or distributed.
        bpy.ops.object.convert(target='MESH')
        finish_mesh(obj,MODEL_COLL,ROOT,mat)


def bolt(name, p, radius=.018):
    return sphere(name,p,radius,steel_dark,seg=12,rings=6)


def tank_vessel(name, x, z, height, radius, rad_large):
    bottom = -height/2 + (.13 if rad_large else .09)
    top = height/2 - (.13 if rad_large else .09)
    cylinder(name+'_Pressure_Body',(x,bottom,z),(x,top,z),radius,tank_metal,vertices=56 if rad_large else 40,bevel=radius*.13)
    for f in (.035,.50,.965):
        y=bottom+(top-bottom)*f
        cylinder(name+'_Bronze_Collar',(x,y-.012,z),(x,y+.012,z),radius*1.012,bronze,
                 vertices=56 if rad_large else 40,bevel=.004)
    cylinder(name+'_Upper_Valve',(x,top-.01,z),(x,top+.055,z),min(.055,radius*.27),bronze,vertices=20)
    cylinder(name+'_Lower_Valve',(x,bottom-.055,z),(x,bottom+.01,z),min(.055,radius*.27),steel_dark,vertices=20)
    # Connection runs to the central service bus.
    cylinder(name+'_Propellant_Line',(x,bottom-.04,z),(0,bottom-.07,0), .013 if rad_large else .008, bronze,vertices=16)


def battery_bank(name, sides, face_id, rad, height):
    normal,right,rot,apothem=face_coords(sides,face_id,rad)
    face_width=2*rad*math.sin(math.pi/sides)
    width=face_width*.66
    bh=height*.82
    depth=.090 if rad>.8 else .057
    center=normal*(apothem-.108 if rad>.8 else apothem-.071)
    box(name+'_FullHeight_Battery',center,(width,bh,depth),battery_mat,bevel=.020 if rad>.8 else .009,rotation=rot)
    # Detailed silver vertical rails and recessed cooling channels on inward face.
    face_point=center-normal*(depth*.51+.006)
    for f in (-.38,.38):
        x=face_point+right*(width*f)
        cylinder(name+'_Cooling_Rail',x+Vector((0,-bh*.46,0)),x+Vector((0,bh*.46,0)),
                 .012 if rad>.8 else .007,steel,vertices=16)
    # mini green LEDs: 2 strips, staggered rows on each inside face
    for row in range(8):
        for col in (-1,1):
            local_y=(row-3.5)*(bh*.091)
            led_center=face_point+Vector((0,local_y,0))+right*(width*(.24*col))-normal*.007
            sphere(name+'_Green_Status_LED',led_center,.012 if rad>.8 else .0065,
                   led_green,seg=12,rings=6)
    # Copper cable down to lower frame
    wirepos=center+right*(width*.08)
    cylinder(name+'_Power_Line',wirepos+Vector((0,-bh*.47,0)),wirepos+Vector((0,-height*.47,0)),
             .012 if rad>.8 else .007,bronze,vertices=16)


def make_girder():
    n=SPEC['sides']
    rad=SPEC['diameter']*.47  # original RoosterWorks circumradius
    height=SPEC['height']
    half=height*.5
    big=SPEC['diameter']>2
    rails=ring_points(n,rad,0)
    steel_r=.083 if big else .052
    # Connected perimeter: primary columns + rings + diagonal bracing
    for i in range(n):
        p0,p1=rails[i],rails[(i+1)%n]
        for part,pos in [('Primary',p0),('Next',p1)]:
            if part=='Primary':
                cylinder(f'Rail_{i:02}', (pos.x,-half,pos.z),(pos.x,half,pos.z),steel_r,steel,vertices=40)
        for y in (-half, 0, half):
            cylinder(f'FrameRing_{i:02}',(p0.x,y,p0.z),(p1.x,y,p1.z),steel_r*.84,
                     steel,vertices=32)
        t=.78*half
        if i%2==0:
            a=(p0.x,-t,p0.z);b=(p1.x,t,p1.z)
        else:
            a=(p0.x,t,p0.z);b=(p1.x,-t,p1.z)
        cylinder(f'CrossBrace_{i:02}',a,b,steel_r*.42,steel_dark,vertices=28)
        for y in (-half,half):
            box(f'Reinforced_Joint_{i:02}', (p0.x,y*.972,p0.z),
                (.18,.15,.18) if big else (.105,.09,.105),bronze,bevel=.016 if big else .010)
            bolt(f'Joint_Bolt_{i:02}',(p0.x,y*.968+.04,p0.z),.018 if big else .011)
    # Service bus, thin piping and reinforced end plates
    box('Central_Service_Spine',(0,0,0),(.16,height*.80,.16) if big else (.11,height*.80,.11),steel_dark,bevel=.024)
    # Inner end-ring support structure. Octagonal parts have eight radial
    # steel spokes linking each INNER corner to its matching OUTER corner.
    # This prevents the interior octagon from looking unsupported or floating.
    for end_name, y in [('Lower', -half+.073), ('Upper', half-.073)]:
        inner = ring_points(n, rad*.64, y)
        for j in range(n):
            a, b = inner[j], inner[(j+1)%n]
            cylinder(f'{end_name}_InnerRing_Edge_{j:02}', a, b,
                     .026 if big else .016, bronze, vertices=28)

        if n == 8 and ADD_INNER_OCTAGON_SPOKES:
            outer = ring_points(n, rad, y)
            for j in range(n):
                # Stop in the intersection volume of the existing rings.
                # Solid capped cylinders keep the part static and KSP-friendly.
                axis = (outer[j] - inner[j]).normalized()
                a = inner[j] - axis*.010
                b = outer[j] + axis*.010
                cylinder(f'{end_name}_RadialSpoke_{j:02}', a, b,
                         INNER_SPOKE_RADIUS, steel, vertices=28, bevel=.003)
                sphere(f'{end_name}_InnerSpokeJoint_{j:02}', inner[j],
                       INNER_SPOKE_RADIUS*1.45, bronze, seg=20, rings=12)
    # Visual monopropellant vessels: all original capacities are unchanged in configs.
    if PART=='OCTO_XL':
        tank_xy=[(.565*math.cos(math.tau*j/4+.20),.565*math.sin(math.tau*j/4+.20)) for j in range(4)]
    elif PART=='OCTO_MEDIUM':
        tank_xy=[(.53*math.cos(math.tau*j/3),.53*math.sin(math.tau*j/3)) for j in range(3)]
    elif PART=='HEX_LONG':
        tank_xy=[(x,z) for x in (-.202,.202) for z in (-.202,.202)]
    else:
        tank_xy=[(0,0)]
    for i,(x,z) in enumerate(tank_xy):
        tank_vessel(f'Monopropellant_{i+1:02}',x,z,height,SPEC['tank_r'],big)
    # One battery bank per polygon face, always full-height
    for i in range(n):
        battery_bank(f'Battery_Face_{i+1:02}',n,i,rad,height)
    # Readable exterior branding on the front face
    normal,right,rot,apothem=face_coords(n,0,rad)
    badge('RoosterWorks_Identification_Plate',normal,rot,
          normal*(apothem+.075)+Vector((0,height*.15,0)),
          width=.65 if big else .34,height=.21 if big else .13)
    # Optional panel-clad truss as ONE parent transform named ArmorPanels.
    # It is a separate collection and transform, to support later KSP PartVariants.
    for i in range(n):
        normal,right,rot,ap=face_coords(n,i,rad)
        width=2*rad*math.sin(math.pi/n)-(.085 if big else .046)
        panelheight=height-.125
        plate=box(f'ArmorPanel_{i+1:02}', normal*(ap-.021),
                  (width,panelheight,.034 if big else .023),white,
                  group=ARMOR_COLL,owner=ARMOR_ROOT,bevel=.009 if big else .004,rotation=rot)
        for y in (-height*.18,height*.18):
            center=normal*(ap+.012)+Vector((0,y,0))
            halfwidth=width*.47
            cylinder('ArmorGoldSeam',center-right*halfwidth,center+right*halfwidth,
                     .008 if big else .005,bronze,vertices=12,group=ARMOR_COLL,owner=ARMOR_ROOT)
    # KSP node positions for future config export; guides are not render meshes.
    top=new_empty('NODE_top',owner=ROOT,group=GUIDES_COLL)
    top.location.y=half
    bottom=new_empty('NODE_bottom',owner=ROOT,group=GUIDES_COLL)
    bottom.location.y=-half


def polygon_radius(theta, sides, radius):
    sector=math.tau/sides
    midface=round((theta-sector/2)/sector)*sector+sector/2
    return radius*math.cos(math.pi/sides)/math.cos(theta-midface)


def make_adapter():
    n=SPEC['sides'];height=SPEC['height'];half=height*.5
    rb=SPEC['diameter']*.47
    rt=SPEC['diameter']*.5
    # Manifold outer shell (ends left open deliberately for stack pass-through).
    verts=[]
    steps=64
    for y,blend in ((-half,0),(0,.5),(half,1)):
        for i in range(steps):
            theta=math.tau*i/steps
            r=polygon_radius(theta,n,rb)*(1-blend)+rt*blend
            verts.append((r*math.cos(theta),y,r*math.sin(theta)))
    faces=[]
    for band in range(2):
        for i in range(steps):
            a=band*steps+i;b=band*steps+(i+1)%steps
            c=(band+1)*steps+(i+1)%steps;d=(band+1)*steps+i
            faces.append((a,b,c,d))
    mesh=bpy.data.meshes.new('Adapter_Original_Loft_Mesh')
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    obj=bpy.data.objects.new('Octagonal_To_Round_Shell' if n==8 else 'Hexagonal_To_Round_Shell',mesh)
    MODEL_COLL.objects.link(obj)
    obj.parent=ROOT
    apply_material(obj,white)
    for p in mesh.polygons:p.use_smooth=True
    add_bevel(obj,.009,3)
    # Closed rail loops around each connector profile.
    bot=ring_points(n,rb,-half)
    for i in range(n):
        cylinder('Lower_Polygon_EndRing',bot[i],bot[(i+1)%n],.055 if n==8 else .035,steel,vertices=32)
    top=ring_points(32,rt,half)
    for i in range(32):
        cylinder('Upper_Round_EndRing',top[i],top[(i+1)%32],.049 if n==8 else .032,steel,vertices=24)
    for i in range(n):
        theta=(i+.5)*math.tau/n
        pos=Vector((rb*.98*math.cos(theta),-height*.20,rb*.98*math.sin(theta)))
        box('Reinforced_Adapter_Clip',pos,(.090,.085,.09) if n==8 else (.055,.065,.055),bronze,bevel=.007)
    normal,right,rot,ap=face_coords(n,0,rb)
    badge('RoosterWorks_Adapter_ID',normal,rot,normal*(ap+.065),
          width=.40 if n==8 else .24,height=.11 if n==8 else .075)
    for nm,y in [('NODE_top',half),('NODE_bottom',-half)]:
        obj=new_empty(nm,owner=ROOT,group=GUIDES_COLL)
        obj.location.y=y


def setup_preview():
    # A display-only scene; never include its lights/camera in the KSP .mu.
    world=bpy.context.scene.world
    if world is None:
        world=bpy.data.worlds.new('RW_Studio_World')
        bpy.context.scene.world=world
    world.use_nodes=True
    bg=world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value=(.018,.032,.052,1)
        bg.inputs['Strength'].default_value=.7
    h=SPEC['height']
    for nm,loc,power,size in [
        ('Key', (3.6,-4.4,h*.7),1900,3.0),
        ('Fill',(-3.5,-2.0,h*.25),950,3.4),
        ('Rim',(1.7,4.0,h*.5),2200,2.5),
    ]:
        data=bpy.data.lights.new(nm,'AREA');data.energy=power;data.shape='DISK';data.size=size
        obj=bpy.data.objects.new(nm,data);PREVIEW_COLL.objects.link(obj)
        obj.location=loc
        obj.rotation_euler=(Vector((0,0,0))-obj.location).to_track_quat('-Z','Y').to_euler()
    cam=bpy.data.cameras.new('RoosterWorks_Preview_Camera')
    obj=bpy.data.objects.new('RoosterWorks_Preview_Camera',cam)
    PREVIEW_COLL.objects.link(obj)
    obj.location=(SPEC['diameter']*1.9,-SPEC['diameter']*2.55,h*.6)
    obj.rotation_euler=(Vector((0,0,0))-obj.location).to_track_quat('-Z','Y').to_euler()
    cam.type='ORTHO'
    cam.ortho_scale=max(SPEC['height']*1.35,SPEC['diameter']*1.9)
    bpy.context.scene.camera=obj
    scene=bpy.context.scene
    try: scene.render.engine='CYCLES'
    except Exception: pass
    if hasattr(scene,'cycles'):scene.cycles.samples=32
    scene.render.resolution_x=1400
    scene.render.resolution_y=1400
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath=str(OUTPUT_DIR/(PART_ID+'_studio.png'))


def export_fbx():
    bpy.ops.object.select_all(action='DESELECT')
    candidates=[obj for obj in bpy.data.objects if obj.type in {'MESH','EMPTY'} and
                (obj in MODEL_COLL.objects or obj in ARMOR_COLL.objects)]
    for obj in candidates:obj.select_set(True)
    if candidates:bpy.context.view_layer.objects.active=candidates[0]
    path=OUTPUT_DIR/(PART_ID+'_INTERMEDIATE.fbx')
    try:
        bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,
                                  object_types={'MESH','EMPTY'},apply_unit_scale=True,
                                  axis_forward='-Z',axis_up='Y',use_mesh_modifiers=True)
        print('[RW] Wrote intermediate FBX:',path)
    except Exception as exc:
        print('[RW] FBX exporter not available in this Blender installation:',exc)
        print('[RW] Saved .blend remains the main editable source.')


if PART in {'OCTO_25_ADAPTER','HEX_125_ADAPTER'}:
    make_adapter()
else:
    make_girder()

# Authored with Unity-style local Y-up coordinates, but rotate the entire
# model to Blender's standard Z-up world. FBX will convert Z-up back to Y-up
# in Unity/KSP. Children are kept parented to the model root.
ROOT.rotation_euler=(math.pi/2, 0, 0)

ARMOR_COLL.hide_render=not SHOW_ARMOR
ARMOR_COLL.hide_viewport=not SHOW_ARMOR
GUIDES_COLL.hide_render=True
GUIDES_COLL.hide_viewport=True

# Add units and metadata for later KSP config writing.
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene['RW_PART_ID']=PART_ID
scene['RW_ElectricCharge']=SPEC['ec']
scene['RW_MonoPropellant']=SPEC['mono']
scene['RW_KSP_Node_Size']=SPEC['node']
scene['RW_Armor_Visual_Only']=True
scene['RW_Note']='Blender artwork only — convert via Unity/KSP PartTools for .mu.'
if ADD_STUDIO_CAMERA_AND_LIGHTS:
    setup_preview()
if EXPORT_FBX:
    export_fbx()
if AUTO_SAVE_BLEND:
    path=OUTPUT_DIR/(PART_ID+'.blend')
    try:
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        print('[RW] Saved:',path)
    except Exception as exc:
        print('[RW] Could not auto-save .blend:',exc)

print('[RW] FINISHED:',PART_ID)
print('[RW] Output folder:',OUTPUT_DIR)
print('[RW] Armor can be toggled in Outliner: RW_OPTIONAL_ARMOR')
print('[RW] No animation or addon is required for the STATIC model.')
