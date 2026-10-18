# รวมโมเดลทั้งหมดของงาน (assets/models/*.glb) มาวางเรียงในฉากเดียว แล้วบันทึกเป็น assets/koi-models.blend
# ไว้ให้มาร์ชเปิดดูใน Blender: "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" assets/koi-models.blend
import bpy, os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, MODELS, ROOT

reset()
ORDER = [('airliner', 0, 0), ('reefer', -22, -8), ('warehouse', 24, 10), ('dof', 0, 22), ('farmhouse', -24, 18),
         ('xray', 14, -10), ('dolly', 8, -10), ('fishbox', -6, -10), ('bag', -9, -10), ('koi', -12, -10),
         ('person', -14, -10), ('pond', -18, -14), ('trees', 30, -8)]
for name, x, y in ORDER:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(MODELS, name + '.glb'))
    new = [o for o in bpy.data.objects if o not in before]
    tops = [o for o in new if o.parent is None]
    for o in tops:
        o.location.x += x; o.location.y += y
    col = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(col)
    for o in new:
        for c in o.users_collection: c.objects.unlink(o)
        col.objects.link(o)
# ไฟแดด + พื้น ให้เปิดมาเห็นสวยในโหมด Material Preview
sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 3
so = bpy.data.objects.new('Sun', sun); so.rotation_euler = (math.radians(50), 0, math.radians(35)); bpy.context.scene.collection.objects.link(so)
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, -0.01)); bpy.context.active_object.name = 'Ground'
out = os.path.join(ROOT, 'assets', 'koi-models.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
print('SAVED', out)
