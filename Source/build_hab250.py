#!/usr/bin/env python3
"""RW-HAB-250 v0.4.5: solid convex collision hull and seated window banks.

Standard-library-only geometry and .mu export; Pillow is used only for PNG
texture generation. Blender can import the same geometry by running
Source/Blender/create_hab250.py. Units are meters; KSP up is +Y.
"""
from __future__ import annotations
import math
import random
import struct
from pathlib import Path
from dataclasses import dataclass, field
from collections import OrderedDict

ROOT = Path(__file__).resolve().parents[1]
PART = 'RW_HAB_250'
MODELS = ROOT / 'GameData' / 'RoosterWorksStationModules' / 'Models'
TAU = 2 * math.pi
TEXTURES = OrderedDict([
    ('ceramic', (218, 224, 224)),
    ('white',   (239, 239, 228)),
    ('steel',   (119, 138, 151)),
    ('graphite',(42, 57, 69)),
    ('bronze',  (176, 123, 67)),
    ('glass',   (28, 43, 49)),
    ('black',   (18, 28, 36)),
    ('rail',    (199, 210, 211)),
    ('label',   (235, 237, 229)),
    ('crest',   (222, 226, 217)),
    ('hubblanket', (151,113,66)),
    ('detail', (51,66,71)),
    ('cladding', (214,220,215)),
    ('cladding_white', (233,234,221)),
])

@dataclass
class Mesh:
    vertices: list = field(default_factory=list)
    normals: list = field(default_factory=list)
    uvs: list = field(default_factory=list)
    triangles: list = field(default_factory=list)

    def quad(self, points, normals, uv=((0, 0),(1, 0),(1, 1),(0, 1)), reverse=False):
        base = len(self.vertices)
        self.vertices.extend(points)
        self.normals.extend(normals)
        self.uvs.extend(uv)
        if not reverse:
            self.triangles.extend(((base,base+1,base+2),(base,base+2,base+3)))
        else:
            self.triangles.extend(((base,base+2,base+1),(base,base+3,base+2)))

    def triangle(self, points, normals, uv):
        base=len(self.vertices)
        self.vertices.extend(points)
        self.normals.extend(normals)
        self.uvs.extend(uv)
        self.triangles.append((base,base+1,base+2))


def point(radius,theta,y):
    return (radius*math.sin(theta),y,radius*math.cos(theta))


def cylinder_surface(mesh, radius, y0, y1, segments=48, theta0=0, theta1=TAU,
                     u0=0, u1=1):
    for i in range(segments):
        a=theta0+(theta1-theta0)*i/segments
        b=theta0+(theta1-theta0)*(i+1)/segments
        na=(math.sin(a),0,math.cos(a));nb=(math.sin(b),0,math.cos(b))
        u_a=u0+(u1-u0)*i/segments;u_b=u0+(u1-u0)*(i+1)/segments
        mesh.quad((point(radius,a,y0),point(radius,b,y0),point(radius,b,y1),point(radius,a,y1)),
                  (na,nb,nb,na),((u_a,0),(u_b,0),(u_b,1),(u_a,1)))


def annulus(mesh, inner, outer, y, normal_sign=1, segments=48):
    n=(0,normal_sign,0)
    for i in range(segments):
        a=TAU*i/segments;b=TAU*(i+1)/segments
        p=(point(inner,a,y),point(outer,a,y),point(outer,b,y),point(inner,b,y))
        mesh.quad(p,(n,)*4,reverse=normal_sign<0)


def tube(mesh,p0,p1,r=.013,sides=10):
    # Outer handrail with stable perpendicular frame, capped ends not required.
    d=[p1[i]-p0[i] for i in range(3)]
    length=math.sqrt(sum(x*x for x in d))
    d=[x/length for x in d]
    axis=(1,0,0) if abs(d[0])<.85 else (0,0,1)
    def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    def norm(a):
        z=math.sqrt(sum(x*x for x in a));return tuple(x/z for x in a)
    p=norm(cross(axis,d));q=norm(cross(d,p))
    for j in range(sides):
        a=TAU*j/sides;b=TAU*(j+1)/sides
        def pt(base,t):return tuple(base[i]+r*(math.cos(t)*p[i]+math.sin(t)*q[i]) for i in range(3))
        def nor(t):return tuple(math.cos(t)*p[i]+math.sin(t)*q[i] for i in range(3))
        # Fix outward normals/winding via geometry triangle orientation.
        mesh.quad((pt(p0,a),pt(p0,b),pt(p1,b),pt(p1,a)),(nor(a),nor(b),nor(b),nor(a)))


# --- v0.2.0 Exterior geometry: realistic Orbital-series, flush end bulkheads ---

def flat_panel(mesh, center_angle, y0, y1, width, radius, segments=8):
    cylinder_surface(mesh, radius, y0, y1, segments=segments,
                     theta0=center_angle-width/2, theta1=center_angle+width/2)


def radial_fastener(mesh, theta, y, radius=1.226, head=.016):
    # Short fastener rivet with normal perpendicular to the cylindrical shell.
    tube(mesh, point(radius,theta,y), point(radius+.010,theta,y),r=head,sides=8)


def square_window_shape(center, y, half_width, half_height, radius=1.22, chamfer=.045):
    """Almost-square viewport with four small clipped corners, NO trapezoid.

    Half-width and half-height are in metres. The window follows the curved
    hull using an angular x coordinate from a physical width at radius 1.22m;
    straight sides remain parallel and upper and lower edges are equally wide.
    Four 4.5% corner bevels soften the geometry but retain a square silhouette.
    """
    assert half_width > 0 and half_height > 0
    assert abs(half_width-half_height) < .004, 'Window must be square'
    a = half_width / radius
    h = half_height
    c = chamfer
    coords = [(-1+c,-1),(1-c,-1),(1,-1+c),(1,1-c),
              (1-c,1),(-1+c,1),(-1,1-c),(-1,-1+c)]
    return [(center+a*x, y+h*yy) for x,yy in coords]


def subdivided_frame_outline(outline, steps=12):
    """Subdivide each edge in angle/y space before projecting to cylinder.

    The original eight chamfered points are still the design silhouette;
    smoothing the *edge projection* only avoids wide flat triangle chords.
    """
    result=[]
    for i,(angle,yy) in enumerate(outline):
        an,yn=outline[(i+1)%len(outline)]
        count=steps if abs(an-angle)>.07 else 1
        for j in range(count):
            t=j/count
            result.append((angle+(an-angle)*t,yy+(yn-yy)*t))
    return result


def window_frame_ring(mesh,outer,inner,r_outer,r_inner):
    """Physical bevel ring: outer reinforced hull -> recessed aperture."""
    assert len(outer)==len(inner)
    # Subdivision applies only to the 8-corner window/hatch polygons;
    # 136/192-point conformal foundations already sample every boundary.
    if len(outer)==8:
        outer=subdivided_frame_outline(outer)
        inner=subdivided_frame_outline(inner)
    assert len(outer)==len(inner)
    for i in range(len(outer)):
        j=(i+1)%len(outer)
        p=(point(r_outer,*outer[i]),point(r_outer,*outer[j]),
           point(r_inner,*inner[j]),point(r_inner,*inner[i]))
        n=tuple((math.sin(t),0,math.cos(t)) for t,_ in
                (outer[i],outer[j],inner[j],inner[i]))
        # Some outlines are clockwise, others counterclockwise. Derive
        # winding geometrically so the visible outside is never culled.
        a=tuple(p[1][k]-p[0][k] for k in range(3))
        b=tuple(p[2][k]-p[0][k] for k in range(3))
        outward=(a[1]*b[2]-a[2]*b[1])*n[0][0]+(a[0]*b[1]-a[1]*b[0])*n[0][2]
        mesh.quad(p,n,reverse=outward<0)


def window_glass(mesh,outline,radius,steps=1):
    """Physical blue-grey tinted glass, curved into the cylindrical shell."""
    cx=sum(t for t,_ in outline)/len(outline)
    cy=sum(yy for _,yy in outline)/len(outline)
    amin=min(t for t,_ in outline);amax=max(t for t,_ in outline)
    ymin=min(yy for _,yy in outline);ymax=max(yy for _,yy in outline)
    def uv(t,yy):return ((t-amin)/(amax-amin),(yy-ymin)/(ymax-ymin))
    # Project every subdivided vertex onto the cylinder, not just a fan's
    # corners. Wide fan chords previously cut through the backing surface.
    for i in range(len(outline)):
        j=(i+1)%len(outline)
        t1,y1=outline[i];t2,y2=outline[j]
        def sample(a,b):
            return (cx+(t1-cx)*a/steps+(t2-cx)*b/steps,
                    cy+(y1-cy)*a/steps+(y2-cy)*b/steps)
        def emit(coords):
            area=(coords[1][0]-coords[0][0])*(coords[2][1]-coords[0][1])-(coords[1][1]-coords[0][1])*(coords[2][0]-coords[0][0])
            if area<0:coords=(coords[0],coords[2],coords[1])
            mesh.triangle(tuple(point(radius,t,yy) for t,yy in coords),
                          tuple((math.sin(t),0,math.cos(t)) for t,yy in coords),
                          tuple(uv(t,yy) for t,yy in coords))
        for a in range(steps):
            for b in range(steps-a):
                emit((sample(a,b),sample(a+1,b),sample(a,b+1)))
                if a+b<steps-1:
                    emit((sample(a+1,b),sample(a+1,b+1),sample(a,b+1)))


# Window and hatch assembly geometry. The standard and hatch assembly are
# mutually exclusive child GameObjects in the generated native KSP .mu.
# That is important: using two whole part configs would break saved craft IDs.
SPECIAL_BAY = (2, 1) # lower/front (+60 degrees) of the six current bays
WINDOW_SCALE = 1.5    # physical width AND height relative to v0.2.2
BAYS = {(2,1),(2,5),(2,9),(5,1),(5,5),(5,9)}


def bay_openings():
    for row,col in sorted(BAYS):
        center=TAU*(col+1)/12
        y=-1.730+(row+.5)*(3.460/8)
        yield center-.732,center+.732,y-.710*.5*1.100,y+.710*.5*1.100


def clipped_hull_panel(mesh,center,y0,y1,width,radius):
    """Cut the complete bank footprint from every overlapping hull course."""
    rectangles=[(center-width/2,center+width/2,y0,y1)]
    for a,b,c,d in bay_openings():
        remaining=[]
        for x0,x1,z0,z1 in rectangles:
            l,r=max(x0,a),min(x1,b)
            bottom,top=max(z0,c),min(z1,d)
            if l>=r or bottom>=top:
                remaining.append((x0,x1,z0,z1));continue
            for rectangle in ((x0,l,z0,z1),(r,x1,z0,z1),
                              (l,r,z0,bottom),(l,r,top,z1)):
                if rectangle[1]-rectangle[0]>1e-7 and rectangle[3]-rectangle[2]>1e-7:
                    remaining.append(rectangle)
        rectangles=remaining
    for a,b,c,d in rectangles:
        cylinder_surface(mesh,radius,c,d,segments=max(1,math.ceil((b-a)/.025)),theta0=a,theta1=b)


def window_bay_foundation(meshes, center, y, panel_height):
    """Flush curved mounting foot directly on the cylindrical pressure hull.

    v0.2.6 BUG: window_rect_outline yielded ONLY EIGHT points across a huge
    +-0.702 rad window bay. window_frame_ring triangulated their straight
    connecting edges into a FLAT CHORD. At 2.5m diameter the midspan chord
    sat >20 cm inside the cylinder, producing flying triangular cheek plates
    and detached raised edges at oblique viewing angles. More trim can't fix it.

    This builds 4 curved, tightly nested continuous contours. Every vertex
    lies on its own cylindrical angle and has a deliberate radial stand-off.
    The foundation is therefore conformal even between window frames.
    """
    half_y=panel_height*.5
    steps=(
        # coating, outer angle/height/radius, inner angle/height/radius
        ('ceramic', .733, half_y*1.102, 1.2048, .703, half_y*1.031, 1.2048),
        ('ceramic', .703, half_y*1.031, 1.2048, .683, half_y*.961, 1.2048),
        ('white',   .683, half_y*.961, 1.2048, .660, half_y*.897, 1.2048),
        ('steel',   .660, half_y*.897, 1.2048, .644, half_y*.858, 1.2040),
    )
    for material,ao,ho,ro,ai,hi,ri in steps:
        outside=curved_rect_contour(center,y,ao,ho,arc_steps=72,side_steps=24)
        inside=curved_rect_contour(center,y,ai,hi,arc_steps=72,side_steps=24)
        window_frame_ring(meshes[material],outside,inside,ro,ri)
    # Curved inset face behind the pressure viewports; no planar quad across
    # the two panel lanes, no physically exposed floating right/left struts.
    cylinder_surface(meshes['ceramic'],1.198,y-panel_height*.433,
                     y+panel_height*.433,segments=88,
                     theta0=center-.646,theta1=center+.646)
    for offs in (-.665,.665):
        for dy in (-.245,.245):
            radial_fastener(meshes['steel'],center+offs,y+dy,
                            radius=1.2048,head=.004)


def curved_rect_contour(center, y, half_angle, half_height, arc_steps=54, side_steps=18):
    """Closed, high-resolution four-sided frame contour on the cylinder.

    Unlike connecting only the four corners with planar quads, every point on
    the upper and lower lips has its OWN polar angle and corresponding 3-D
    cylindrical position. This prevents the top and bottom portions of the
    gasket from bridging empty space as a straight chord when viewed above.
    """
    assert arc_steps >= 12 and side_steps >= 4
    result=[]
    for j in range(arc_steps):
        t=-half_angle+2*half_angle*j/arc_steps
        result.append((center+t,y+half_height))
    for j in range(side_steps):
        yy=half_height-2*half_height*j/side_steps
        result.append((center+half_angle,y+yy))
    for j in range(arc_steps):
        t=half_angle-2*half_angle*j/arc_steps
        result.append((center+t,y-half_height))
    for j in range(side_steps):
        yy=-half_height+2*half_height*j/side_steps
        result.append((center-half_angle,y+yy))
    assert len(result)==2*(arc_steps+side_steps)
    return result


def panoramic_pressure_bay(meshes, center, y, panel_height):
    """Three enlarged square viewports with shallow seated frames and curved glass.

    Pane apertures are exactly 1.5 times prior width and height, not merely
    a 50% increase in area. Center spacing is widened to prevent overlap.
    All outlines and backing use geometry original to RoosterWorks.
    """
    window_bay_foundation(meshes,center,y,panel_height)
    for offset in (-.421,0,.421):
        def pane(half_size):
            return square_window_shape(center+offset,y,half_size,half_size)
        outer_plate=pane(.160*WINDOW_SCALE)
        white_rim=pane(.143*WINDOW_SCALE)
        inner_bevel=pane(.127*WINDOW_SCALE)
        rubber_seal=pane(.113*WINDOW_SCALE)
        aperture=pane(.104*WINDOW_SCALE)
        window_frame_ring(meshes['white'],outer_plate,white_rim,1.2048,1.2070)
        window_frame_ring(meshes['rail'],white_rim,inner_bevel,1.2070,1.2040)
        window_frame_ring(meshes['graphite'],inner_bevel,rubber_seal,1.2040,1.2020)
        window_frame_ring(meshes['black'],rubber_seal,aperture,1.2020,1.2010)
        window_glass(meshes['glass'],aperture,1.2015,steps=8)
    # The new foundation is already a true four-sided curved surround.
    # Do not stack the old cosmetic surround on top: it produced side wings.


def hatch_pressure_bay(meshes, center, y, panel_height):
    """Original modeled side pressure hatch replacing a single 3-pane bank.

    Hatch leaf, reinforced surround, hinges, latch wheel and sealed glass
    porthole are meshes, not borrowed textures. This *initial* KSP prototype
    provides the physical appearance only: no validated EVA airlock collider.
    """
    window_bay_foundation(meshes,center,y,panel_height)
    # Hatch ring is also curved from the hull outwards; avoid old flat
    # eight-point backing and any overlaid disconnected supporting wings.
    # Wider base is covered by the conformal window_bay_foundation above.
    hatch_rims=(
        ('ceramic',.410,.407,1.199,.374,.372,1.209),
        ('white',  .374,.372,1.209,.352,.345,1.219),
        ('steel',  .352,.345,1.219,.340,.333,1.218),
    )
    for mat,ao,ho,ro,ai,hi,ri in hatch_rims:
        window_frame_ring(meshes[mat],
            curved_rect_contour(center,y,ao,ho,arc_steps=48,side_steps=20),
            curved_rect_contour(center,y,ai,hi,arc_steps=48,side_steps=20),
            ro,ri)
    cylinder_surface(meshes['ceramic'],1.202,y-.342,y+.342,segments=48,
                     theta0=center-.335,theta1=center+.335)
    outline=lambda h:square_window_shape(center,y,h,h,radius=1.22,chamfer=.085)
    # Squared pressure-door surround with a recessed dark peripheral gasket.
    window_frame_ring(meshes['ceramic'],outline(.353),outline(.335),1.216,1.222)
    window_frame_ring(meshes['white'],outline(.335),outline(.312),1.222,1.226)
    window_frame_ring(meshes['steel'],outline(.312),outline(.289),1.227,1.233)
    window_frame_ring(meshes['graphite'],outline(.289),outline(.274),1.233,1.232)
    # Leaf as a curved opaque pressure plate with brushed white finish.
    cylinder_surface(meshes['white'],1.236,y-.269,y+.269,segments=28,
                     theta0=center-.266,theta1=center+.266)
    # Narrow horizontal embossments around the circular view port.
    for yy in (y-.203,y+.203):
        cylinder_surface(meshes['steel'],1.240,yy-.007,yy+.007,segments=18,
                         theta0=center-.230,theta1=center+.230)
    # Original pressure porthole: rounded glazing inside a metal annular rim.
    def circle(radius,sections=28):
        return [(center+(radius/1.22)*math.sin(TAU*k/sections),
                 y+radius*math.cos(TAU*k/sections)) for k in range(sections)]
    window_frame_ring(meshes['steel'],circle(.159),circle(.142),1.244,1.246)
    window_frame_ring(meshes['graphite'],circle(.142),circle(.118),1.247,1.246)
    window_frame_ring(meshes['black'],circle(.118),circle(.108),1.247,1.243)
    window_glass(meshes['glass'],circle(.108),1.244,steps=8)
    # Mechanical hinges at left, latch lever at right. These are not functional
    # KSP EVA interactions until a tested airlock transform is introduced.
    for yy in (y-.179,y+.179):
        t=center-.292
        tube(meshes['steel'],point(1.247,t,yy-.041),
             point(1.247,t,yy+.041),r=.029,sides=10)
        tube(meshes['rail'],point(1.251,t,yy-.063),
             point(1.251,t,yy+.063),r=.011,sides=8)
    t=center+.290
    tube(meshes['steel'],point(1.247,t,y-.110),
         point(1.247,t,y+.110),r=.021,sides=10)
    tube(meshes['graphite'],point(1.255,t,y-.033),
         point(1.268,t+.030,y-.033),r=.019,sides=10)
    for dx in (-.222,.222):
        for dy in (-.218,.218):
            radial_fastener(meshes['steel'],center+dx,y+dy,radius=1.243,head=.012)


def equipment_bay(meshes,theta,y):
    """Recessed exterior service enclosure rather than a flat painted tile."""
    flat_panel(meshes['graphite'],theta,y-.192,y+.192,.385,1.209)
    flat_panel(meshes['steel'],theta,y-.164,y+.164,.353,1.218)
    flat_panel(meshes['ceramic'],theta,y-.122,y+.122,.295,1.224)
    for dy in (-.10,-.055,.055,.10):
        flat_panel(meshes['graphite'],theta,y+dy-.004,y+dy+.004,.205,1.234)
    for dy in (-.148,.148):
        for dth in (-.153,.153):
            radial_fastener(meshes['bronze'],theta+dth,y+dy,radius=1.229,head=.012)
    flat_panel(meshes['bronze'],theta+.150,y-.069,y+.069,.014,1.24,segments=2)


def recessed_bulkhead(meshes,sign):
    from station_endcaps import add_endcap
    add_endcap(meshes,sign,1.980)


def generate_groups():
    meshes={key:Mesh() for key in TEXTURES}
    standard={key:Mesh() for key in TEXTURES}
    hatch={key:Mesh() for key in TEXTURES}
    # One coherent cylindrical pressurized shell, not a stack of exposed disks.
    cylinder_surface(meshes['graphite'],1.187,-1.82,1.82,segments=96)
    # Layered micrometeorite shielding: 12 axial lanes, 8 panel courses.
    # Every observation cluster spans TWO panel lanes; real square windows
    # replace old flat rectangular window 'decals' and preserve the cylinder silhouette.
    cols=12;rows=8
    bays=BAYS
    equipment_tiles={(1,3),(6,7)}
    y_min=-1.730; pitch=3.460/rows
    for row in range(rows):
        y0=y_min+row*pitch+.014
        y1=y_min+(row+1)*pitch-.014
        for col in range(cols):
            center=TAU*(col+.5)/cols
            width=TAU/cols-.027
            if (row,col) in bays:
                bay_center=TAU*(col+1)/cols
                destination=standard if (row,col)==SPECIAL_BAY else meshes
                # Bay overhangs one adjoining hull course vertically to house
                # 1.5x larger panes while keeping existing bank positions.
                panoramic_pressure_bay(destination,bay_center,(y0+y1)*.5,.710)
                if (row,col)==SPECIAL_BAY:
                    hatch_pressure_bay(hatch,bay_center,(y0+y1)*.5,.710)
            if (row,col) in equipment_tiles:
                equipment_bay(meshes,center,(y0+y1)/2)
                continue
            material='cladding_white' if (row+3*col)%11==0 else 'cladding'
            clipped_hull_panel(meshes[material],center,y0,y1,width,1.204)
            if (row+col)%3==0:
                clipped_hull_panel(meshes['steel'],center,y0,y0+.009,width-.040,1.212)
            if row in (0,3,7) and col%2==0:
                for sign in (-1,1):
                    t=center+sign*(width/2-.021); yy=y0+.036
                    if not any(a<t<b and c<yy<d for a,b,c,d in bay_openings()):
                        radial_fastener(meshes['steel'],t,yy)
    # Slim, flush station-to-station junction rings. The old 0.12m dark
    # bands visually doubled up when two habitats were stacked, looking like
    # a thick docking port. The new narrow perimeter stripes stay entirely
    # INSIDE each Â±1.980m stack plane and are cosmetic, not docking ports.
    cylinder_surface(meshes['steel'],1.214,-.016,.016,segments=96)
    cylinder_surface(meshes['bronze'],1.223,-.003,.003,segments=96)
    for sign in (-1,1):
        lo,hi=(1.730,1.980) if sign>0 else (-1.980,-1.730)
        cylinder_surface(meshes['ceramic'],1.200,lo,hi,segments=96)
        # Thin graphite & bronze seams across the module shoulders.
        for center,half,mat,rad in ((1.811,.010,'graphite',1.218),
                                    (1.811,.0025,'bronze',1.223),
                                    (1.956,.016,'steel',1.214),
                                    (1.956,.004,'bronze',1.222)):
            a,b=(center-half,center+half) if sign>0 else (-center-half,-center+half)
            cylinder_surface(meshes[mat],rad,a,b,segments=96)
    # Recessed end bulkheads: stay INSIDE module length, no mushroom collars.
    for sign in (-1,1):recessed_bulkhead(meshes,sign)
    # Handrails. The lower front-right rail (k=1) crosses the cosmetic
    # hatch. It must belong to the selectable variant, NOT to the Base mesh.
    # Standard retains the original full-length rail. SideHatch replaces it
    # with the dedicated grab rails and footholds below.
    def rail_segment(group,theta,lo,hi):
        r=1.258
        tube(group['rail'],point(r,theta,lo),point(r,theta,hi),r=.013,sides=8)
        for yy in (lo,hi):
            tube(group['steel'],point(1.213,theta,yy),point(r,theta,yy),r=.022,sides=8)
    for k in range(8):
        theta=TAU*(k+.5)/8
        rail_segment(meshes,theta,.38,1.50)
        if k==1:
            rail_segment(standard,theta,-1.50,-.38)
            # No shortened center rail through the new footholds.
        else:
            rail_segment(meshes,theta,-1.50,-.38)
    # Side Hatch grab rails and two footholds, aligned with the functional
    # ladder below. Render-only hardware cannot obstruct the stock EVA ray.
    hatch_angle=TAU/6
    for offset in (-.30,.30):
        rail_segment(hatch,hatch_angle+offset,-1.43,-.12)
    for yy in (-1.36,-1.13):
        for step in range(8):
            a=hatch_angle-.30+.60*step/8
            b=hatch_angle-.30+.60*(step+1)/8
            tube(hatch['rail'],point(1.258,a,yy),
                 point(1.258,b,yy),r=.013,sides=8)
    # Branded rooster crest: its own texture on an inset hull plaque.
    # Upper front location remains visible when the lower window bank becomes
    # the hatch; the mirrored back-of-station text label remains separately.
    logo_theta=TAU/6  # +60 degrees, above the front upper window cluster
    flat_panel(meshes['graphite'],logo_theta,1.220,1.572,.323,1.214,segments=16)
    flat_panel(meshes['bronze'],logo_theta,1.240,1.553,.298,1.222,segments=16)
    flat_panel(meshes['crest'],logo_theta,1.253,1.540,.275,1.229,segments=16)
    for off in (-.141,.141):
        for yy in (1.257,1.540):
            radial_fastener(meshes['steel'],logo_theta+off,yy,radius=1.234,head=.009)
    # RCS-style and sensor electronics inset in surface (decorative only).
    for theta in (0,TAU/3,2*TAU/3):
        for y in (-1.58,1.58):
            flat_panel(meshes['graphite'],theta,y-.095,y+.095,.190,1.222)
            for offset in (-.046,.046):
                flat_panel(meshes['black'],theta+offset,y-.052,y+.052,.066,1.229)
            radial_fastener(meshes['bronze'],theta,y,radius=1.239,head=.013)
    # Thin articulated access cover with inset RoosterWorks identification texture.
    # Center points toward model -Z, to distinguish brand view from windows.
    th=math.pi
    flat_panel(meshes['graphite'],th,-.284,.286,.741,1.227,segments=12)
    flat_panel(meshes['bronze'],th,-.269,.271,.715,1.235,segments=12)
    flat_panel(meshes['label'],th,-.248,.250,.682,1.245,segments=12)
    for sign in (-1,1):
        for dy in (-.215,.215):radial_fastener(meshes['graphite'],th+sign*.324,dy,radius=1.253,head=.013)
    from exterior_detail import add_hab
    add_hab(meshes)
    from surface_uv import finish
    finish(meshes);finish(standard);finish(hatch)
    return {'Base':meshes,'WindowBankStandard':standard,'SideHatch':hatch}


def combine_meshes(*layers):
    """Merged export for artist inspection without variant overlap in OBJ."""
    combined={key:Mesh() for key in TEXTURES}
    for layer in layers:
        for name,src in layer.items():
            dst=combined[name]
            offset=len(dst.vertices)
            dst.vertices.extend(src.vertices)
            dst.normals.extend(src.normals)
            dst.uvs.extend(src.uvs)
            dst.triangles.extend(tuple(i+offset for i in tri) for tri in src.triangles)
    return combined


def generate_geometry(variant='Standard'):
    groups=generate_groups()
    assert variant in ('Standard','SideHatch')
    return combine_meshes(groups['Base'],groups['WindowBankStandard' if variant=='Standard' else 'SideHatch'])


def rooster_crest_image(size=512):
    """Original, crisp RoosterWorks rooster insignia; no third-party art."""
    from PIL import Image, ImageDraw
    upscale=3
    N=size*upscale
    im=Image.new('RGB',(N,N),(234,235,226))
    d=ImageDraw.Draw(im)
    def P(v):return round(v*N/512)
    def pts(vertices):return [(P(x),P(y)) for x,y in vertices]
    def ellipse(box,**kw):d.ellipse(tuple(P(t) for t in box),**kw)
    def poly(points,**kw):d.polygon(pts(points),**kw)
    def line(points,**kw):d.line(pts(points),**kw)
    # inset circular graphite disk with bronze perimeter
    ellipse((12,12,500,500),fill=(173,121,65))
    ellipse((30,30,482,482),fill=(34,47,56))
    ellipse((49,49,463,463),outline=(226,221,205),width=P(4))
    white=(239,238,220); red=(175,55,45); copper=(210,152,80)
    # stylized swept feathers / tail silhouette (five ascending points)
    poly([(160,320),(128,295),(88,227),(84,172),(122,198),(137,226),
          (112,178),(119,119),(157,175),(180,218),(169,173),(194,141),
          (209,211),(228,250),(214,325)],fill=white)
    poly([(184,315),(212,255),(269,230),(307,235),(340,275),(325,320),
          (284,351),(246,362),(208,347)],fill=white)
    # Comb is distinct RoosterWorks red, so silhouette reads as a rooster
    poly([(294,232),(283,189),(299,166),(313,192),(319,155),(337,175),
          (339,201),(357,189),(363,216),(341,246)],fill=red)
    # Head, long neck, face, beak and wattle
    poly([(307,228),(344,224),(365,237),(369,261),(363,279),(347,290),
          (332,308),(325,319),(307,291),(316,271)],fill=white)
    poly([(368,246),(397,255),(370,266)],fill=copper)
    ellipse((353,249,361,257),fill=(30,39,44))
    poly([(361,271),(378,288),(359,299),(347,289)],fill=red)
    # Legs, claw footprints and sharp short spur
    line([(273,350),(269,408),(247,428)],fill=copper,width=P(11),joint='curve')
    line([(302,339),(311,405),(329,421)],fill=copper,width=P(11),joint='curve')
    line([(247,428),(278,426),(290,421)],fill=copper,width=P(8))
    line([(299,422),(330,422),(343,430)],fill=copper,width=P(8))
    line([(267,404),(251,388)],fill=copper,width=P(7))
    # Small side feather incisions, emphasizing original vector drawing
    line([(238,293),(258,302),(279,298)],fill=(160,178,179),width=P(5),joint='curve')
    line([(237,313),(255,325),(279,326)],fill=(160,178,179),width=P(5),joint='curve')
    return im.resize((size,size),Image.Resampling.LANCZOS)


def make_textures(dest=MODELS):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    dest=Path(dest); dest.mkdir(parents=True,exist_ok=True)
    for index,(name,rgb) in enumerate(TEXTURES.items()):
        rng=random.Random(240221+index)
        if name=='crest':
            im=rooster_crest_image()
        elif name=='label':
            im=Image.new('RGB',(1024,512),(222,227,223));d=ImageDraw.Draw(im)
            d.rectangle((10,10,1012,500),outline=(151,104,49),width=19)
            d.rectangle((38,38,984,472),outline=(50,69,80),width=5)
            for x in (65,960):
                for y in (70,444):d.ellipse((x-7,y-7,x+7,y+7),fill=(103,113,123))
            try:
                bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',76)
                small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',60)
            except OSError:bold=ImageFont.load_default();small=bold
            d.text((85,115),'ROOSTERWORKS',font=bold,fill=(28,43,58))
            emblem=rooster_crest_image(120)
            im.paste(emblem,(866,94))
            d.line((83,230,933,230),fill=(174,123,67),width=8)
            d.text((83,301),'RW-HAB-250 / ORBITAL',font=small,fill=(95,70,48))
        else:
            im=Image.new('RGB',(512,512));pix=im.load()
            for yy in range(512):
                for xx in range(512):
                    fine=rng.randint(-5,5)
                    long=2.4*math.sin(xx*.045)+1.2*math.sin(yy*.036)
                    if name=='glass':
                        # Desaturated grey-green sealed pressure glass, not a
                        # saturated blue glossy electronic display.
                        u=xx/511.0;v=yy/511.0
                        long=(1-v)*5.0+(1-u)*1.0
                        fine=int(fine*.25)
                    if name in ('ceramic','white'):long+=2.4*math.sin(xx*.22)
                    if name=='bronze':long+=4*math.sin(xx*.061)
                    if name=='glass':
                        top=1-yy/511.0
                        base=(21+9*top,38+9*top,43+8*top)
                        pix[xx,yy]=tuple(max(0,min(255,int(v+long*.5+fine))) for v in base)
                    else:
                        pix[xx,yy]=tuple(max(0,min(255,int(v+long+fine))) for v in rgb)
            d=ImageDraw.Draw(im)
            if name in ('ceramic','white'):
                for yy in range(31,510,93):
                    d.line((0,yy,511,yy),fill=tuple(max(0,v-6) for v in rgb),width=1)
            if name in ('steel','rail'):
                for yy in range(14,512,31):
                    d.line((0,yy,511,yy),fill=tuple(min(255,v+7) for v in rgb),width=1)
            if name=='graphite':
                for yy in range(0,512,90):d.line((0,yy,511,yy),fill=(60,78,88),width=2)
            if name=='glass':
                # Fine glancing reflection instead of opaque neon-blue stripes.
                # Layers are blended into the surface to avoid sticker styling.
                overlay=Image.new('RGBA',(512,512),(0,0,0,0))
                shine=ImageDraw.Draw(overlay)
                shine.polygon([(82,0),(124,0),(279,512),(237,512)],
                              fill=(157,174,177,12))
                shine.polygon([(360,0),(369,0),(507,512),(498,512)],
                              fill=(194,202,203,7))
                shine.line((36,53,479,53),fill=(165,179,181,8),width=5)
                overlay=overlay.filter(ImageFilter.GaussianBlur(12))
                im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB')
        im.save(dest/f'rwm_{name}.png',optimize=True)
    # Separate emissive mask: glass still looks dark when off. KSP stock
    # ModuleColorChanger drives _EmissiveColor when the user toggles the lights.
    # This texture belongs ONLY to the glass material: never glow the hull,
    # rooster decal, handrails or dark gaskets.
    emit=Image.new('RGB',(512,512))
    epx=emit.load()
    for yy in range(512):
        for xx in range(512):
            # Warm white with subtle edge darkening; intentionally no neon.
            x=(xx-255.5)/255.5; y=(yy-255.5)/255.5
            edge=max(0.70,1.0-0.16*(x*x+y*y))
            epx[xx,yy]=(int(250*edge),int(230*edge),int(194*edge))
    emit.save(dest/'rwm_cabin_emissive.png',optimize=True)


class Writer:
    def __init__(self,path):self.handle=Path(path).open('wb')
    def i(self,*v):self.handle.write(struct.pack('<'+'i'*len(v),*v))
    def f(self,*v):self.handle.write(struct.pack('<'+'f'*len(v),*v))
    def b(self,n):self.handle.write(bytes((n,)))
    def s(self,st):
        data=st.encode('utf-8');n=len(data)
        while n>=128:self.b(n&127|128);n>>=7
        self.b(n);self.handle.write(data)
    def xyz(self,p):self.f(*p)
    def close(self):self.handle.close()


def node(w,name,pos=(0,0,0),collider=None,rot=(0,0,0,1),
         tag='Untagged', layer=0, trigger=False):
    """Create a KSP MU transform, optional box collider, and tag/layer.

    EVA is driven by an *actual* Unity trigger collider tagged Airlock on
    physics layer 21 ('Part Triggers'). The visual door alone cannot EVA.
    """
    w.s(name);w.xyz(pos);w.f(*rot);w.xyz((1,1,1))
    w.i(24);w.s(tag);w.i(layer)
    if collider is not None:
        w.i(28);w.b(1 if trigger else 0);w.xyz(collider);w.xyz((0,0,0))


def hull_collision_mesh():
    """One closed convex prism, 96 triangles (below Unity's convex limit).

    KSP starts the outward hatch ray 0.5 m behind the hatch. A hollow
    collection of thin wall boxes presents a false obstruction to that ray.
    A solid convex volume contains its origin, as on conventional pods.
    """
    mesh=Mesh()
    cylinder_surface(mesh,1.204,-1.980,1.980,segments=24)
    for sign in (-1,1):
        for k in range(24):
            a,b=TAU*k/24,TAU*(k+1)/24
            points=((0,sign*1.980,0),point(1.204,a,sign*1.980),point(1.204,b,sign*1.980))
            if sign<0:points=(points[0],points[2],points[1])
            mesh.triangle(points,((0,sign,0),)*3,((0,0),)*3)
    return mesh


def write_mesh(w,mesh):
    w.i(13,len(mesh.vertices),1);w.i(14)
    for p in mesh.vertices:w.xyz(p)
    w.i(15)
    for uv in mesh.uvs:w.f(*uv)
    w.i(17)
    for n in mesh.normals:w.xyz(n)
    w.i(19,len(mesh.triangles)*3)
    for triangle in mesh.triangles:w.i(*triangle)
    w.i(22)


def create_mu(groups,path):
    """KSP model with two *real* toggleable Unity transform names."""
    w=Writer(path)
    w.i(76543,5);w.s(PART);node(w,PART)
    def emit_material_meshes(meshes, group_name):
        for mat_id,(mat,mesh) in enumerate(meshes.items()):
            if not mesh.triangles:continue
            assert len(mesh.vertices)<65535
            # Unique names allow stock ModuleColorChanger to target glass
            # in each variant without affecting all other part renderers.
            label='RW_'+mat.title().replace('_','')
            if mat=='glass':label='RW_Glass'+group_name
            w.i(0);node(w,label)
            w.i(7);w.i(13,len(mesh.vertices),1);w.i(14)
            for p in mesh.vertices:w.xyz(p)
            w.i(15)
            for u,v in mesh.uvs:w.f(u,v)
            w.i(17)
            for n in mesh.normals:w.xyz(n)
            w.i(19,len(mesh.triangles)*3)
            for t in mesh.triangles:w.i(*t)
            w.i(22);w.i(8);w.b(1);w.b(1);w.i(1,mat_id);w.i(1)
    emit_material_meshes(groups['Base'],'Base')
    for name in ('WindowBankStandard','SideHatch'):
        w.i(0);node(w,name)
        emit_material_meshes(groups[name], 'Standard' if name=='WindowBankStandard' else name)
        w.i(1)
    # RW-HAB-250 experimental EVA airlock: a real PartTriggers (layer 21)
    # box trigger tagged 'Airlock'. The selected side hatch sits at the
    # lower front, angle 60deg and Y ~ -0.649 m, where the 3-pane window
    # bank used to be. Orient local +Z *outward* along the surface normal.
    # Position beyond the hull (r=1.43 m; visual hatch ~r=1.24m), leaving
    # clearance for the Kerbal's body and for KSP's obstruction raycasts.
    # Native triggers stay outside visual variants for Part.Awake discovery.
    # ModuleRWStationHatch gates both triggers and the cached airlock after
    # variant selection, including editor changes and flight loading.
    row,col=SPECIAL_BAY
    hatch_angle=TAU*(col+1)/12
    pitch=3.460/8
    hatch_y=(-1.730+row*pitch+.014 + -1.730+(row+1)*pitch-.014)*.5
    airlock_rotation=(0,math.sin(hatch_angle/2),0,math.cos(hatch_angle/2))
    w.i(0)
    node(w,'RW_HAB250_EVA_Airlock',
         pos=point(1.43,hatch_angle,hatch_y),
         collider=(.72,.78,.40),rot=airlock_rotation,
         tag='Airlock',layer=21,trigger=True)
    w.i(1)
    # KSP aligns Kerbal forward with ladder +Z, so face INTO the hull.
    # Local +Y is climb-up. Its center shares the proven clear EVA position
    # and its volume covers the exit and the visible rails/footholds.
    ladder_angle=hatch_angle+math.pi
    w.i(0)
    node(w,'RW_HAB250_EVA_Ladder',
         pos=point(1.43,hatch_angle,hatch_y),
         collider=(.86,1.64,.70),
         rot=(0,math.sin(ladder_angle/2),0,math.cos(ladder_angle/2)),
         tag='Ladder',layer=21,trigger=True)
    w.i(1)
    w.i(0);node(w,'RW_HAB250_SolidHullCollider')
    w.i(25);w.b(0);w.b(1) # MeshCollider2: non-trigger, convex
    write_mesh(w,hull_collision_mesh())
    w.i(1)
    w.i(10,len(TEXTURES))
    for mat in TEXTURES:
        w.s('RW_'+mat)
        w.s('KSP/Emissive/Diffuse' if mat=='glass' else 'KSP/Diffuse')
        w.i(4 if mat=='glass' else 2)
        w.s('_Color');w.i(0);w.f(1,1,1,1)
        w.s('_MainTex');w.i(4,list(TEXTURES).index(mat));w.f(1,1);w.f(0,0)
        if mat=='glass':
            w.s('_EmissiveColor');w.i(0);w.f(0,0,0,1)
            w.s('_Emissive');w.i(4,len(TEXTURES));w.f(1,1);w.f(0,0)
    w.i(12,len(TEXTURES)+1)
    for mat in TEXTURES:w.s('rwm_'+mat);w.i(0)
    w.s('rwm_cabin_emissive');w.i(0)
    w.close()


def create_obj(meshes,path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.with_suffix('.mtl').write_text(''.join(
        f'newmtl RW_{m}\nKa 0.3 0.3 0.3\nKd 1.0 1.0 1.0\nKs 0.15 0.15 0.15\nmap_Kd ../../GameData/RoosterWorksStationModules/Models/rwm_{m}.png\n\n'
        for m in TEXTURES),encoding='utf-8')
    with path.open('w',encoding='utf-8') as f:
        f.write(f'# RoosterWorks original procedural 2.5m station habitat; units meters\nmtllib {path.with_suffix(".mtl").name}\n')
        ofs=0
        for material,mesh in meshes.items():
            f.write(f'o {material}\nusemtl RW_{material}\n')
            for v in mesh.vertices:f.write('v %0.6f %0.6f %0.6f\n'%v)
            for uv in mesh.uvs:f.write('vt %0.6f %0.6f\n'%uv)
            for n in mesh.normals:f.write('vn %0.6f %0.6f %0.6f\n'%n)
            for tri in mesh.triangles:
                f.write('f '+' '.join('%d/%d/%d'%(t+ofs+1,t+ofs+1,t+ofs+1) for t in tri)+'\n')
            ofs+=len(mesh.vertices)


def main():
    groups=generate_groups()
    meshes=combine_meshes(groups['Base'],groups['WindowBankStandard'])
    alt=combine_meshes(groups['Base'],groups['SideHatch'])
    assert sum(len(m.triangles) for m in meshes.values())>8500
    make_textures(MODELS)
    create_mu(groups,MODELS/(PART+'.mu'))
    create_obj(meshes,ROOT/'Source'/'Blender'/(PART+'.obj'))
    create_obj(alt,ROOT/'Source'/'Blender'/(PART+'_SideHatch.obj'))
    print('Model built:',PART)
    print('Triangles, standard:',sum(len(m.triangles) for m in meshes.values()))
    print('Triangles, side hatch:',sum(len(m.triangles) for m in alt.values()))
    print('Native KSP model bytes:',(MODELS/(PART+'.mu')).stat().st_size)

if __name__=='__main__': main()
