# ตัวช่วยที่สคริปต์ Blender ทุกตัวใช้ร่วมกัน
# วิธีรัน (ตัวอย่าง):
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python tools/blender/make_airliner.py
# ทุกสคริปต์ล้างฉากก่อน สร้างโมเดลด้วยโค้ด แล้วส่งออกเป็น .glb ไปที่ assets/models/ และเรนเดอร์ภาพตัวอย่างไปที่ assets/previews/
import bpy, bmesh, math, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS = os.path.join(ROOT, 'assets', 'models')
PREVIEWS = os.path.join(ROOT, 'assets', 'previews')


_mats = {}


def reset():
    """ล้างฉากให้ว่าง (ไม่เหลือกล้อง ไฟ ลูกบาศก์เริ่มต้น)"""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()   # วัสดุเก่าถูกลบไปพร้อมฉากแล้ว ต้องล้างที่จำไว้ด้วย


def mat(name, rgb, rough=0.6, metal=0.0, alpha=1.0):
    """วัสดุสีเดียว (rgb เป็นค่า 0..1 แบบที่ตาเห็น) ใช้ซ้ำตามชื่อ"""
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    # Blender เก็บสีแบบ linear: แปลงจากสีที่ตาเห็น (sRGB) ก่อน
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    p.inputs['Base Color'].default_value = (*lin, 1.0)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if alpha < 1.0:
        p.inputs['Alpha'].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            m.blend_method = 'BLEND'
    _mats[name] = m
    return m


def hexrgb(h):
    return ((h >> 16) & 255) / 255, ((h >> 8) & 255) / 255, (h & 255) / 255


def obj_from_bmesh(name, bm, material, smooth=False, parent=None):
    """สร้างวัตถุจาก bmesh แล้วใส่วัสดุ"""
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(material)
    for poly in me.polygons:
        poly.use_smooth = smooth
    if parent is not None:
        ob.parent = parent
    return ob


def prim(kind, name, material, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, smooth=False, **kw):
    """สร้างรูปทรงพื้นฐาน (cube / cylinder / uv_sphere / cone / torus)"""
    getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=loc, rotation=rot, **kw)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(material)
    for poly in ob.data.polygons:
        poly.use_smooth = smooth
    if parent is not None:
        ob.parent = parent
    return ob


def root(name):
    """วัตถุว่างเป็นตัวแม่ของทั้งโมเดล (ส่งออกเป็นโหนดเดียว)"""
    ob = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def export_glb(filename):
    """ส่งออกทั้งฉากเป็น .glb (แกน +Y ขึ้นแบบ glTF) — ใช้ค่าสี/วัสดุ ไม่มีภาพ texture"""
    os.makedirs(MODELS, exist_ok=True)
    path = os.path.join(MODELS, filename)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=False,
                              export_apply=True, export_yup=True, export_cameras=False, export_lights=False)
    print('EXPORTED', path, os.path.getsize(path))
    return path


def render_preview(filename, cam_loc, target=(0, 0, 0), lens=50, size=(960, 540)):
    """เรนเดอร์ภาพตัวอย่าง (ไว้ให้มาร์ชดู) ด้วยไฟแดด + พื้นสีเทาอ่อน"""
    os.makedirs(PREVIEWS, exist_ok=True)
    sc = bpy.context.scene
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'):
        try:
            sc.render.engine = eng
            break
        except Exception:
            continue
    sc.render.resolution_x, sc.render.resolution_y = size
    world = bpy.data.worlds.new('w'); world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.62, 0.78, 0.92, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.8
    sc.world = world
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.5
    so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    sc.collection.objects.link(so)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(mat('ground_preview', (0.78, 0.8, 0.82)))
    cam = bpy.data.cameras.new('cam'); cam.lens = lens
    co = bpy.data.objects.new('cam', cam); co.location = cam_loc
    sc.collection.objects.link(co)
    tgt = bpy.data.objects.new('tgt', None); tgt.location = target; sc.collection.objects.link(tgt)
    c = co.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    sc.camera = co
    sc.render.filepath = os.path.join(PREVIEWS, filename)
    bpy.ops.render.render(write_still=True)
    print('PREVIEW', sc.render.filepath)
