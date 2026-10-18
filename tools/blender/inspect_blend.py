# ดูว่าในไฟล์ .blend มีวัตถุอะไรบ้าง (ชื่อ ชนิด จำนวนหน้า ขนาด) — รันด้วย blender --background --disable-autoexec ไฟล์.blend --python นี้
import bpy
for o in bpy.data.objects:
    faces = len(o.data.polygons) if o.type == 'MESH' else 0
    print('OBJ', o.name, o.type, faces, tuple(round(d, 2) for d in o.dimensions), [m.name for m in o.material_slots] if o.type == 'MESH' else '')
print('IMAGES', [(i.name, i.filepath) for i in bpy.data.images])
