"""Builds the low-poly set pieces for the dress-up scenes and exports them as FBX.

  blender --background --python make_scene_props.py -- <out_dir>

Everything is coloured with vertex colours (M_PropVertexColor in Unreal), in the soft pastel
of the painted backgrounds. Sizes in metres; the character stands at the origin, the camera
looks along -Y from +Y.

  SM_Podium         round stone platform the character stands on (5 cm high, 70 cm radius)
  SM_Petal          one sakura petal, for the falling petals
  SM_PetalsGround   petals strewn on the ground and on the podium
  SM_FlowerClump    grass tuft with small white and pink flowers
  SM_Stone          small rounded stone
  SM_Winter_Podium     the podium under snow, a few stones showing
  SM_Winter_SnowPile   low lumpy heap of snow
  SM_Winter_SnowBush   round bush with snow on top
  SM_Winter_Snowflake  six-armed flake, for falling snow
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

out_dir = sys.argv[sys.argv.index("--") + 1]
os.makedirs(out_dir, exist_ok=True)
rng = random.Random(7)

PODIUM_R = 0.70
PODIUM_H = 0.05


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def colour(hex_or_rgb, jitter=0.0):
    r, g, b = hex_or_rgb
    if jitter:
        k = 1.0 + rng.uniform(-jitter, jitter)
        r, g, b = (min(1.0, max(0.0, c * k)) for c in (r, g, b))
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)


class Builder:
    """Collects faces with one colour each into a bmesh."""

    def __init__(self):
        self.bm = bmesh.new()
        self.col = self.bm.loops.layers.color.new("Col")

    def face(self, points, rgba):
        verts = [self.bm.verts.new(p) for p in points]
        f = self.bm.faces.new(verts)
        for loop in f.loops:
            loop[self.col] = rgba
        return f

    def finish(self, name):
        me = bpy.data.meshes.new(name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        obj = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(obj)
        return obj


def petal_points(length, width, cup=0.25):
    """Teardrop petal in its XY plane, tip at +X, slightly cupped up, notched at the tip like sakura."""
    # Simple outline: base, two sides, notched tip.
    outline = [
        (0.00, 0.00), (0.25, -0.38), (0.60, -0.50), (0.92, -0.30), (1.00, -0.08),
        (0.90, 0.00), (1.00, 0.08), (0.92, 0.30), (0.60, 0.50), (0.25, 0.38),
    ]
    return [Vector((u * length, v * width, cup * width * (abs(v) / 0.5) ** 2)) for u, v in outline]


def add_petal(b, matrix, tint):
    outline = petal_points(0.032, 0.026)
    centre = Vector((0.016, 0, 0))
    pink = colour(tint, 0.06)
    pale = colour((min(1, tint[0] + 0.05), min(1, tint[1] + 0.12), min(1, tint[2] + 0.1)))
    for i in range(len(outline)):
        a, c = outline[i], outline[(i + 1) % len(outline)]
        f = b.face([matrix @ centre, matrix @ a, matrix @ c], pink)
        f.loops[0][b.col] = pale


PETAL_PINKS = [(0.98, 0.72, 0.80), (0.96, 0.78, 0.86), (1.0, 0.84, 0.89), (0.94, 0.66, 0.76)]


SNOW = (0.97, 0.98, 1.0)
SNOW_SHADE = (0.86, 0.89, 0.97)


def make_podium(name="SM_Podium", snow=0.0):
    """snow: share of the stones covered by snow (the rest show through)."""
    b = Builder()
    seg = 48
    rings = [0.0, 0.30, 0.52, PODIUM_R - 0.05, PODIUM_R]
    heights = [PODIUM_H + 0.004, PODIUM_H + 0.003, PODIUM_H + 0.002, PODIUM_H, PODIUM_H - 0.012]
    cream = (0.97, 0.92, 0.88)
    # Top: concentric bands of flagstones, every stone a little different. Each of the seg slices
    # of a band belongs to one stone (slice * stones // seg), so the band is always closed.
    def p(rad, h, a):
        return Vector((rad * math.cos(a), rad * math.sin(a), h))

    for r in range(len(rings) - 1):
        stones = 1 if r == 0 else (12 if r == 1 else 20)
        band = (0.93, 0.86, 0.83) if r == 2 else cream
        stone_cols = [colour(SNOW, 0.02) if rng.random() < snow else colour(band, 0.035) for _ in range(stones)]
        for i in range(seg):
            rgba = stone_cols[i * stones // seg]
            a0 = 2 * math.pi * i / seg
            a1 = 2 * math.pi * (i + 1) / seg
            if r == 0:
                b.face([p(0, heights[0], 0), p(rings[1], heights[1], a0), p(rings[1], heights[1], a1)], rgba)
            else:
                b.face([p(rings[r], heights[r], a0), p(rings[r + 1], heights[r + 1], a0),
                        p(rings[r + 1], heights[r + 1], a1), p(rings[r], heights[r], a1)], rgba)
    # Rounded rim down to the ground.
    side = [(PODIUM_R, PODIUM_H - 0.012), (PODIUM_R + 0.008, PODIUM_H - 0.025), (PODIUM_R + 0.012, 0.0)]
    rim = colour(SNOW_SHADE) if snow > 0 else colour((0.88, 0.80, 0.78))
    for i in range(seg):
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        for j in range(len(side) - 1):
            (r0, h0), (r1, h1) = side[j], side[j + 1]
            b.face([Vector((r0 * math.cos(a0), r0 * math.sin(a0), h0)), Vector((r0 * math.cos(a1), r0 * math.sin(a1), h0)),
                    Vector((r1 * math.cos(a1), r1 * math.sin(a1), h1)), Vector((r1 * math.cos(a0), r1 * math.sin(a0), h1))], rim)
    bmesh.ops.remove_doubles(b.bm, verts=b.bm.verts, dist=0.0001)
    return b.finish(name)


def make_petal():
    b = Builder()
    # Falling petals are seen from a few metres away: twice the size of the ones on the ground.
    add_petal(b, Matrix.Diagonal((2.0, 2.0, 2.0, 1)) @ Matrix.Translation((-0.016, 0, 0)), PETAL_PINKS[1])
    return b.finish("SM_Petal")


def make_petals_ground():
    b = Builder()
    placed = 0
    while placed < 320:
        # Denser near the podium, thinning out; only in front of and beside it (what the camera sees).
        r = PODIUM_R * 0.2 + abs(rng.gauss(0, 0.9))
        a = rng.uniform(-math.pi, math.pi)
        x, y = r * math.cos(a), r * math.sin(a)
        if y < -1.2 or abs(x) > 2.6:
            continue
        z = (PODIUM_H + 0.006) if r < PODIUM_R - 0.03 else 0.004
        if PODIUM_R - 0.03 <= r <= PODIUM_R + 0.03:
            continue
        m = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rng.uniform(0, 2 * math.pi), 4, "Z") \
            @ Matrix.Rotation(rng.uniform(-0.25, 0.25), 4, "X")
        add_petal(b, m, rng.choice(PETAL_PINKS))
        placed += 1
    return b.finish("SM_PetalsGround")


def make_flower_clump():
    b = Builder()
    greens = [(0.62, 0.80, 0.52), (0.70, 0.86, 0.58), (0.56, 0.76, 0.50)]
    for _ in range(22):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0, 0.09)
        base = Vector((r * math.cos(a), r * math.sin(a), 0))
        h = rng.uniform(0.07, 0.14)
        lean = Vector((rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), 0))
        w = rng.uniform(0.012, 0.02)
        side = Vector((math.cos(a + 1.57), math.sin(a + 1.57), 0)) * w
        tip = base + lean + Vector((0, 0, h))
        g = colour(rng.choice(greens), 0.05)
        f = b.face([base - side, base + side, tip], g)
        f.loops[2][b.col] = colour((0.82, 0.92, 0.66))
    flower_cols = [(1.0, 1.0, 0.97), (1.0, 0.86, 0.90), (1.0, 0.95, 0.99)]
    for _ in range(9):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0.0, 0.09)
        top = Vector((r * math.cos(a), r * math.sin(a), rng.uniform(0.08, 0.15)))
        stem = colour((0.58, 0.76, 0.50))
        b.face([Vector((top.x - 0.002, top.y, 0)), Vector((top.x + 0.002, top.y, 0)), top], stem)
        petal_col = colour(rng.choice(flower_cols), 0.03)
        tilt = Matrix.Rotation(rng.uniform(-0.4, 0.4), 4, "X") @ Matrix.Rotation(rng.uniform(-0.4, 0.4), 4, "Y")
        for k in range(5):
            ang = 2 * math.pi * k / 5
            m = Matrix.Translation(top) @ tilt @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Diagonal((0.85, 0.85, 0.85, 1))
            add_petal(b, m, (1, 1, 1))
        # The five petals just added (10 triangles each) take the flower's colour.
        for f in list(b.bm.faces)[-50:]:
            for loop in f.loops:
                loop[b.col] = petal_col
        heart = colour((1.0, 0.85, 0.35))
        b.face([top + Vector((0.004, 0, 0.003)), top + Vector((-0.002, 0.0035, 0.003)), top + Vector((-0.002, -0.0035, 0.003))], heart)
    return b.finish("SM_FlowerClump")


def make_stone():
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.06)
    for v in bm.verts:
        v.co.x *= 1.3
        v.co.z *= 0.55
        v.co *= 1.0 + rng.uniform(-0.08, 0.08)
    for v in bm.verts:
        v.co.z = max(v.co.z, -0.005)
    col = bm.loops.layers.color.new("Col")
    for f in bm.faces:
        rgba = colour((0.80, 0.77, 0.80), 0.05)
        for loop in f.loops:
            loop[col] = rgba
    me = bpy.data.meshes.new("SM_Stone")
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("SM_Stone", me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def lumpy(name, radius, squash, colours, subdiv=2, wobble=0.12, flat_bottom=0.0):
    """A soft heap: an icosphere squashed and wobbled, cut flat at the ground."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    for v in bm.verts:
        v.co.z *= squash
        v.co *= 1.0 + rng.uniform(-wobble, wobble)
        v.co.z = max(v.co.z, flat_bottom)
    col = bm.loops.layers.color.new("Col")
    top = max(v.co.z for v in bm.verts)
    for f in bm.faces:
        # Lighter on top, the shade colour lower down.
        hgt = f.calc_center_median().z / max(top, 1e-4)
        rgba = colour(colours[0] if hgt > 0.45 else colours[1], 0.02)
        for loop in f.loops:
            loop[col] = rgba
    for f in bm.faces:
        f.smooth = True  # snow is soft, not faceted
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_snow_pile():
    return lumpy("SM_Winter_SnowPile", 0.10, 0.38, (SNOW, SNOW_SHADE), subdiv=3, wobble=0.06)


def make_snow_bush():
    """Dark green lumps with snow caps."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    for _ in range(5):
        tmp = bmesh.new()
        r = rng.uniform(0.09, 0.14)
        bmesh.ops.create_icosphere(tmp, subdivisions=2, radius=r)
        off = Vector((rng.uniform(-0.12, 0.12), rng.uniform(-0.08, 0.08), r * 0.7 + rng.uniform(0, 0.08)))
        for v in tmp.verts:
            v.co = v.co * (1.0 + rng.uniform(-0.1, 0.1)) + off
        me_tmp = bpy.data.meshes.new("tmp")
        tmp.to_mesh(me_tmp)
        tmp.free()
        start = len(bm.faces)
        bm.from_mesh(me_tmp)
        bpy.data.meshes.remove(me_tmp)
        bm.faces.ensure_lookup_table()
        for f in bm.faces[start:]:
            n = f.normal if f.normal.length > 0 else Vector((0, 0, 1))
            rgba = colour(SNOW, 0.02) if f.calc_center_median().z > off.z + r * 0.25 else colour((0.36, 0.52, 0.42), 0.06)
            for loop in f.loops:
                loop[col] = rgba
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new("SM_Winter_SnowBush")
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("SM_Winter_SnowBush", me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_snowflake():
    """Flat six-armed star, 5 cm, white."""
    b = Builder()
    white = colour(SNOW)
    for k in range(6):
        a = math.pi / 3 * k
        d = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-d.y, d.x, 0)) * 0.003
        b.face([side * 1.5, d * 0.025 + side, d * 0.025 - side, -side * 1.5], white)
        mid = d * 0.014
        for t in (1, -1):
            br = Vector((math.cos(a + t * 0.8), math.sin(a + t * 0.8), 0)) * 0.008
            b.face([mid - side, mid + br, mid + side], white)
    return b.finish("SM_Winter_Snowflake")


bpy.ops.wm.read_homefile(use_empty=True)
objs = [make_podium(), make_petal(), make_petals_ground(), make_flower_clump(), make_stone(),
        make_podium("SM_Winter_Podium", snow=0.8), make_snow_pile(), make_snow_bush(), make_snowflake()]
for obj in objs:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    path = os.path.join(out_dir, obj.name + ".fbx")
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, mesh_smooth_type="FACE" if not obj.name.startswith("SM_Winter_Snow") or obj.name.endswith("flake") else "EDGE",
                             colors_type="SRGB", add_leaf_bones=False, bake_anim=False)
    print("PROP", obj.name, len(obj.data.vertices), [round(v, 3) for v in obj.dimensions])
