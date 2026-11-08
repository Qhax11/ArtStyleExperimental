# Unreal MCP tool script (ProgrammaticToolset.execute_tool_script): imports the items listed in
# Saved/DressUpImport/items_<FILE>.json, indices START..END. Prepend FILE/START/END lines when sending.
# Per item: skeletal mesh, one material instance per slot and variant, icon, DA_<Name>.
import json

AT = 'editor_toolset.toolsets.asset.AssetTools.'
SM = 'editor_toolset.toolsets.skeletal_mesh.SkeletalMeshTools.'
MI = 'editor_toolset.toolsets.material_instance.MaterialInstanceTools.'
TX = 'editor_toolset.toolsets.texture.TextureTools.'
OB = 'editor_toolset.toolsets.object.ObjectTools.'
DA = 'editor_toolset.toolsets.data_asset.DataAssetTools.'

ROOT = '/Game/DressUp/Items/VRoid'
BUILT = 'D:/Projects/ArtStyleExperimental/SourceAssets/VRoid/built'
SKEL = '/Game/DressUp/Character/SKEL_evrar_full.SKEL_evrar_full'
CHAR = '/Game/DressUp/Character/Materials/'
EXTRA = '/Game/DressUp/Items/Extras/Materials/'
PARENTS = {
    'cloth': CHAR + 'MI_N00_004_01_Tops_01_CLOTH__Instance_.MI_N00_004_01_Tops_01_CLOTH__Instance_',
    'hair': EXTRA + 'MI_N00_000_Hair_00_HAIR__Instance_.MI_N00_000_Hair_00_HAIR__Instance_',
    'hat': EXTRA + 'MI_Accessory_BaseballCap_01_CLOTH__Instance_.MI_Accessory_BaseballCap_01_CLOTH__Instance_',
    'frame': EXTRA + 'MI_Accessory_GlassesLowFrame_01_MATCAP__Instance_.MI_Accessory_GlassesLowFrame_01_MATCAP__Instance_',
    'lens': EXTRA + 'MI_Accessory_GlassesLowLens_01_MATCAP__Instance_.MI_Accessory_GlassesLowLens_01_MATCAP__Instance_',
}


def t(n, a):
    return execute_tool(n, json.dumps(a))['returnValue']


def ref(path):
    name = path.rsplit('/', 1)[1]
    return {'refPath': path + '.' + name}


def exists(path):
    return t(AT + 'exists', {'path': path})


def parent_for(item, i):
    if item['kind'] == 'hair':
        return PARENTS['hair']
    if item['slot'] == 'Glasses':
        return PARENTS['frame'] if i == 0 else PARENTS['lens']
    if item['slot'] == 'Hat':
        return PARENTS['hat']
    return PARENTS['cloth']


def tex(h):
    return ref(ROOT + '/Textures/T_P_' + h)


def make_mi(item, v, i, s):
    path = ROOT + '/Materials/MI_%s_V%d_M%d' % (item['name'], v, i)
    if exists(path):
        return ref(path)
    mi = t(MI + 'create', {'folder_path': ROOT + '/Materials', 'asset_name': path.rsplit('/', 1)[1],
                           'parent': {'refPath': parent_for(item, i)}})
    for p in ('gltf_tex_diffuse', 'mtoon_tex_Shade'):
        t(MI + 'set_texture_parameter', {'instance': mi, 'name': p, 'value': tex(s['tex'])})
    sh = s['shade']
    t(MI + 'set_vector_parameter', {'instance': mi, 'name': 'mtoon_ShadeColor',
                                    'value': {'r': sh[0], 'g': sh[1], 'b': sh[2], 'a': 1}})
    if s.get('alpha') == 'MASK':
        t(MI + 'set_scalar_parameter', {'instance': mi, 'name': 'mtoon_Cutoff', 'value': s.get('cutoff', 0.5)})
    if s.get('normal'):
        n = tex(s['normal'])
        t(OB + 'set_properties', {'instance': n, 'properties': {'CompressionSettings': 'TC_Normalmap', 'SRGB': False}})
        for p in ('mtoon_tex_Normal', 'gltf_tex_normal'):
            t(MI + 'set_texture_parameter', {'instance': mi, 'name': p, 'value': n})
    return mi


def import_item(item):
    name = item['name']
    folder = ROOT + '/' + item['slot']
    mesh_path = folder + '/SK_' + name
    if not exists(mesh_path):
        t(SM + 'import_file', {'folder_path': folder, 'asset_name': 'SK_' + name,
                               'source_file': BUILT + '/SK_' + name + '.fbx',
                               'skeleton': {'refPath': SKEL}, 'import_materials': False})
    mesh = ref(mesh_path)
    slots = t(SM + 'get_material_slots', {'mesh': mesh})
    looks = []
    for v, variant in enumerate(item['variants']):
        mats = [make_mi(item, v, i, s) for i, s in enumerate(variant['slots'])]
        looks.append(mats)
    # Variant materials in the mesh's own slot order.
    order = [int(s.rsplit('_M', 1)[1]) for s in slots]
    for slot_name, i in zip(slots, order):
        t(SM + 'set_material', {'mesh': mesh, 'slot_name': slot_name, 'material': looks[0][i]})
    icon_path = '/Game/DressUp/UI/Icons/VRoid/T_Icon_' + name
    if not exists(icon_path):
        t(TX + 'import_file', {'folder_path': '/Game/DressUp/UI/Icons/VRoid', 'asset_name': 'T_Icon_' + name,
                               'source_file': item['icon']})
        t(OB + 'set_properties', {'instance': ref(icon_path), 'properties': {
            'CompressionSettings': 'TC_EditorIcon', 'LODGroup': 'TEXTUREGROUP_UI',
            'MipGenSettings': 'TMGS_NoMipmaps', 'NeverStream': True}})
    da_path = '/Game/DressUp/Data/VRoid/DA_' + name
    if not exists(da_path):
        t(DA + 'create', {'folder_path': '/Game/DressUp/Data/VRoid', 'asset_name': 'DA_' + name,
                          'asset_type': {'refPath': '/Script/ArtStyleExperimental.DressUpItem'}})
    variants = []
    if len(looks) > 1:
        for v, variant in enumerate(item['variants']):
            sw = variant['swatch']
            variants.append({'swatch': {'r': sw[0], 'g': sw[1], 'b': sw[2], 'a': 1},
                             'materials': [looks[v][i] for i in order]})
    t(OB + 'set_properties', {'instance': ref(da_path), 'properties': {
        'DisplayName': item['display'], 'Icon': ref(icon_path), 'Slot': item['slot'],
        'SkeletalMesh': mesh, 'HiddenBodyRegions': item['hidden'], 'BlockedSlots': item['blocked'],
        'Variants': variants}})
    return da_path


def run():
    items = json.loads(t(AT + 'read_file', {'file_path': 'D:/Projects/ArtStyleExperimental/Saved/DressUpImport/items_%d.json' % FILE}))
    done, errors = [], []
    for item in items[START:END]:
        try:
            done.append(import_item(item))
        except Exception as e:
            errors.append(item['name'] + ': ' + str(e)[:300])
    t(AT + 'save_assets', {'asset_paths': []})
    return {'done': len(done), 'total': len(items), 'errors': errors}
