# เครื่องบินลำตัวกว้างแบบ Boeing 787-8 (ย่อส่วน ×0.45) สร้างด้วยโค้ดใน Blender แล้วส่งออก assets/models/airliner.glb
# ตำแหน่งให้ตรงกับฉากเว็บ: หัวเครื่องไปทาง +X, แกนลำตัวสูง 3.0, ประตูห้องสินค้าอยู่ด้าน -Y ของ Blender (= ด้าน +z ในเว็บ) ที่ x = 8
# ไม่มีโลโก้สายการบินจริง (ใช้สีกลาง ๆ: ลำตัวขาว ท้องเทา หางแดง)
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, obj_from_bmesh, prim, root, export_glb, render_preview

reset()
WHITE = mat('white', hexrgb(0xf4f6f8), 0.35)
BELLY = mat('belly', hexrgb(0xb9c0c9), 0.5)
DARK = mat('window', hexrgb(0x1d2b3a), 0.2)
GREY = mat('metal', hexrgb(0x9aa3ae), 0.35, 0.6)
RED = mat('tail', hexrgb(0xd9423e), 0.4)
TYRE = mat('tyre', hexrgb(0x22262c), 0.9)
DOOR = mat('door', hexrgb(0x5d6876), 0.5)

plane = root('Airliner')
L = 25.6          # ความยาวทั้งลำ
R = 1.5           # รัศมีลำตัว
CY = 3.0          # ความสูงแกนลำตัว
X0 = -12.0        # ปลายหาง (x น้อยสุด) → หัวที่ X0 + L

def profile(t):
    """รัศมีและการยกของลำตัวที่ตำแหน่ง t (0 = หาง, 1 = หัว): หัวมน หางเรียวและเชิดขึ้น"""
    if t > 0.88:                       # จมูก: โค้งแบบวงรี
        k = (t - 0.88) / 0.12
        return R * math.sqrt(max(0.0, 1 - k * k)) * 0.98 + 0.02, -0.25 * k
    if t < 0.22:                       # หาง: เรียวลงและยกขึ้น
        k = (0.22 - t) / 0.22
        return R * (1 - 0.82 * k), 0.95 * k * k
    return R, 0.0

# ลำตัว: วงแหวน 28 เหลี่ยม × 48 ช่วง แล้วเชื่อมเป็นผิว
bm = bmesh.new()
rings, seg = 48, 28
for i in range(rings + 1):
    t = i / rings
    r, lift = profile(t)
    x = X0 + t * L
    ring = []
    for j in range(seg):
        a = 2 * math.pi * j / seg
        ring.append(bm.verts.new((x, math.cos(a) * r, CY + lift + math.sin(a) * r * 1.04)))
    if i:
        for j in range(seg):
            bm.faces.new((prev[j], prev[(j + 1) % seg], ring[(j + 1) % seg], ring[j]))
    prev = ring
bm.normal_update()
body = obj_from_bmesh('Fuselage', bm, WHITE, smooth=True, parent=plane)

# ท้องเครื่องสีเทา (ครึ่งล่างตรงกลางลำ) — แผ่นโค้งบาง ๆ แปะทับผิวลำตัว
bm = bmesh.new()
prev = None
for i in range(23):
    x = X0 + L * (0.22 + 0.62 * i / 22)
    ring = [bm.verts.new((x, math.cos(a) * R * 1.006, CY + math.sin(a) * R * 1.046))
            for a in [math.pi * (1.18 + 0.64 * j / 10) for j in range(11)]]
    if prev:
        for j in range(10):
            bm.faces.new((prev[j], prev[j + 1], ring[j + 1], ring[j]))
    prev = ring
obj_from_bmesh('Belly', bm, BELLY, smooth=True, parent=plane)

# หน้าต่างห้องโดยสาร (แถบจุดเล็ก ๆ ทั้งสองข้าง) + กระจกห้องนักบิน
for side in (1, -1):
    for k in range(34):
        x = X0 + L * 0.27 + k * 0.44
        prim('cube', 'Window', DARK, loc=(x, side * R * 1.0, CY + 0.45), scale=(0.11, 0.03, 0.15), parent=plane)
    prim('cube', 'Cockpit', DARK, loc=(X0 + L * 0.955, side * 0.55, CY + 0.5), rot=(0, math.radians(-28), side * math.radians(25)),
         scale=(0.35, 0.03, 0.17), parent=plane)

def wing(name, root_x, root_chord, tip_chord, span, sweep, dihedral, thick, z0, material, side):
    """ปีกแบบลู่ (มีความหนาแบบแพนอากาศอย่างง่าย) side = +1 / -1"""
    bm = bmesh.new()
    def section(x_le, chord, y, z, th):
        # 6 จุดรอบแพนอากาศ: ขอบหน้า บน/ล่าง กลาง และขอบหลัง
        pts = [(0.0, 0.0), (0.12, 0.55), (0.45, 0.5), (1.0, 0.0), (0.45, -0.32), (0.12, -0.3)]
        return [bm.verts.new((x_le - c * chord, y, z + h * th)) for c, h in pts]
    tip_x = root_x - math.tan(math.radians(sweep)) * span
    a = section(root_x, root_chord, 0, z0, thick)
    b = section(tip_x, tip_chord, side * span, z0 + math.tan(math.radians(dihedral)) * span, thick * 0.35)
    n = len(a)
    for i in range(n):
        bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(list(reversed(a))); bm.faces.new(b)
    bm.normal_update()
    return obj_from_bmesh(name, bm, material, smooth=False, parent=plane)

for s in (1, -1):
    wing('Wing', 3.2, 6.2, 1.4, 13.4, 32, 6, 0.55, CY - 0.8, WHITE, s)
    wing('Stabilizer', X0 + 4.0, 3.0, 1.0, 4.8, 35, 4, 0.25, CY + 0.9, WHITE, s)
    # เครื่องยนต์ใต้ปีก: ฝาครอบ + ช่องดูดอากาศ + เสาแขวน
    ex, ey = 3.2 - math.tan(math.radians(32)) * 4.7 + 1.2, s * 4.7
    prim('cylinder', 'Nacelle', WHITE, loc=(ex, ey, CY - 1.55), rot=(0, math.radians(90), 0), scale=(1.0, 1.0, 2.1),
         vertices=24, radius=1.0, depth=1.0, smooth=True, parent=plane)
    prim('cylinder', 'Intake', DARK, loc=(ex + 1.06, ey, CY - 1.55), rot=(0, math.radians(90), 0), vertices=24, radius=0.86, depth=0.06, parent=plane)
    prim('cone', 'Exhaust', GREY, loc=(ex - 1.35, ey, CY - 1.55), rot=(0, math.radians(-90), 0), vertices=16, radius1=0.62, radius2=0.25, depth=0.7, parent=plane)
    prim('cube', 'Pylon', WHITE, loc=(ex - 0.1, ey, CY - 0.95), scale=(1.1, 0.12, 0.35), parent=plane)

# หางตั้ง (ลู่ไปข้างหลัง) สีแดง
bm = bmesh.new()
root_pts = [(X0 + 6.2, 0, CY + 1.2), (X0 + 1.4, 0, CY + 1.4)]
tip_pts = [(X0 + 2.6, 0, CY + 5.7), (X0 + 1.0, 0, CY + 5.7)]
th = 0.16
v = [bm.verts.new((x, y + d, z)) for (x, y, z) in root_pts + tip_pts for d in (th, -th)]
# v: r0+,r0-,r1+,r1-,t0+,t0-,t1+,t1-
for f in [(0, 2, 6, 4), (1, 5, 7, 3), (0, 4, 5, 1), (2, 3, 7, 6), (4, 6, 7, 5), (0, 1, 3, 2)]:
    bm.faces.new([v[i] for i in f])
bm.normal_update()
obj_from_bmesh('Fin', bm, RED, parent=plane)

# ล้อ: ล้อหน้า 2 ล้อ, ล้อหลัก 2 ชุด ชุดละ 4 ล้อ
def gear(x, y, wheels):
    prim('cylinder', 'Strut', GREY, loc=(x, y, 0.95), vertices=8, radius=0.09, depth=1.5, parent=plane)
    for dx, dy in wheels:
        prim('cylinder', 'Tyre', TYRE, loc=(x + dx, y + dy, 0.42), rot=(math.radians(90), 0, 0), vertices=16, radius=0.42, depth=0.26, smooth=True, parent=plane)
gear(X0 + L * 0.86, 0, [(0, 0.17), (0, -0.17)])
for s in (1, -1):
    gear(0.2, s * 1.6, [(0.45, 0.2), (0.45, -0.2), (-0.45, 0.2), (-0.45, -0.2)])

# ประตูห้องสินค้า (ด้าน -Y = ด้าน +z ในเว็บ) ที่ x = 8 — ชื่อ HoldDoor ให้เว็บซ่อน/แสดงได้
prim('cube', 'HoldDoor', DOOR, loc=(8.0, -R * 0.99, CY - 0.75), rot=(math.radians(-18), 0, 0), scale=(1.25, 0.04, 0.7), parent=plane)

export_glb('airliner.glb')
render_preview('airliner.png', cam_loc=(26, -30, 14), target=(1, 0, 2.5), lens=45)
