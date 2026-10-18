# แหล่งที่มาของโมเดล 3 มิติ

| ไฟล์ | ชุด | ผู้สร้าง | สัญญาอนุญาต | ที่มา |
|---|---|---|---|---|
| `models/delivery.glb` (รถควบคุมอุณหภูมิ) | Car Kit 3.1 | Kenney (www.kenney.nl) | CC0 1.0 | https://kenney.nl/assets/car-kit |
| `models/van.glb` (รถตู้) | Car Kit 3.1 | Kenney | CC0 1.0 | https://kenney.nl/assets/car-kit |
| `models/tractor.glb` (รถลากในสนามบิน) | Car Kit 3.1 | Kenney | CC0 1.0 | https://kenney.nl/assets/car-kit |
| `models/cone.glb` (กรวยจราจร) | Car Kit 3.1 | Kenney | CC0 1.0 | https://kenney.nl/assets/car-kit |
| `models/Textures/colormap.png` (สีของโมเดลทั้ง 4) | Car Kit 3.1 | Kenney | CC0 1.0 | https://kenney.nl/assets/car-kit |

CC0 = ใช้ได้ทั้งงานเรียน งานส่วนตัว และงานเชิงพาณิชย์ ไม่ต้องขออนุญาตหรือให้เครดิต (Kenney ขอให้ให้เครดิตถ้าทำได้ จึงบันทึกไว้ที่นี่)

ของอื่นในฉาก (เครื่องบิน คน ปลา ถุง กล่องปลา อาคาร บ่อ) สร้างด้วยโค้ดในไฟล์ `Koi_Air_Cargo_3D.html` บล็อก `koi-scene`

## โมเดลที่สร้างเองใน Blender 5.2 (ของงานนี้เอง ไม่มีลิขสิทธิ์บุคคลอื่น)

| ไฟล์ | สร้างจากสคริปต์ | หมายเหตุ |
|---|---|---|
| `models/airliner.glb` | `tools/blender/make_airliner.py` | เครื่องบินลำตัวกว้างแบบ 787-8 ย่อส่วน ×0.45 ไม่มีโลโก้สายการบินจริง |
| `models/koi.glb` | `tools/blender/make_koi.py` | ปลาคาร์ฟ 3 สายพันธุ์ (โคฮากุ ซันเก้ โอกอน) ลวดลายเป็นสีที่จุดยอด |
| `models/person.glb` | `tools/blender/make_person.py` | คนทำงาน สีเสื้อเปลี่ยนตามบทบาทในเว็บ |

ภาพตัวอย่างของแต่ละโมเดลอยู่ใน `previews/` สร้างใหม่ได้ด้วยคำสั่ง (แล้วรัน `npm run inline` เพื่อฝังลงไฟล์เว็บ):

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python tools/blender/make_airliner.py
```

ไฟล์เครื่องบิน `CartoonPlane.zip` (CC0) ที่โหลดมาก่อนหน้า ไม่ได้ใช้ เพราะเป็นเครื่องบินใบพัดลำเล็ก ไม่ใช่เครื่องบินลำตัวกว้าง
