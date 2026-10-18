# แหล่งที่มาของโมเดล 3 มิติ

| ไฟล์ | ชุด | ผู้สร้าง | สัญญาอนุญาต | ที่มา |
|---|---|---|---|---|
| `models/delivery.glb` (รถควบคุมอุณหภูมิ) | Car Kit 3.1 | Kenney (www.kenney.nl) | CC0 1.0 | https://kenney.nl/assets/car-kit |
| `models/van.glb` (รถตู้) | Car Kit 3.1 | Kenney | CC0 1.0 | https://kenney.nl/assets/car-kit |
| `models/tractor.glb` (รถลากในสนามบิน) | Car Kit 3.1 | Kenney | CC0 1.0 | https://kenney.nl/assets/car-kit |
| `models/cone.glb` (กรวยจราจร) | Car Kit 3.1 | Kenney | CC0 1.0 | https://kenney.nl/assets/car-kit |
| `models/Textures/colormap.png` (สีของโมเดลทั้ง 4) | Car Kit 3.1 | Kenney | CC0 1.0 | https://kenney.nl/assets/car-kit |

CC0 = ใช้ได้ทั้งงานเรียน งานส่วนตัว และงานเชิงพาณิชย์ ไม่ต้องขออนุญาตหรือให้เครดิต (Kenney ขอให้ให้เครดิตถ้าทำได้ จึงบันทึกไว้ที่นี่)

ของอื่นในฉาก (โต๊ะ สายพาน เอกสาร ตราประทับ อาคารผู้โดยสาร) สร้างด้วยโค้ดในไฟล์ `Koi_Air_Cargo_3D.html` บล็อก `koi-scene` ส่วนเครื่องบิน ปลา คน กล่องปลา ถุง คลังสินค้า X-ray บ่อ แท่นลาก บ้านฟาร์ม อาคาร DOF และต้นไม้ สร้างใน Blender (ด้านล่าง)

## โมเดลที่สร้างเองใน Blender 5.2 (ของงานนี้เอง ไม่มีลิขสิทธิ์บุคคลอื่น)

| ไฟล์ | สร้างจากสคริปต์ | หมายเหตุ |
|---|---|---|
| `models/airliner.glb` | `tools/blender/make_airliner.py` | เครื่องบินลำตัวกว้างแบบ 787-8 ย่อส่วน ×0.45 ไม่มีโลโก้สายการบินจริง |
| `models/koi.glb` | `tools/blender/make_koi.py` | ปลาคาร์ฟ 3 สายพันธุ์ (โคฮากุ ซันเก้ โอกอน) ลวดลายเป็นสีที่จุดยอด |
| `models/person.glb` | `tools/blender/make_person.py` | คนทำงาน สีเสื้อเปลี่ยนตามบทบาทในเว็บ |
| `models/fishbox.glb` | `tools/blender/make_props.py` | กล่องโฟมใส่ปลา ฝา สายรัด ป้าย LIVE ANIMALS / THIS WAY UP |
| `models/bag.glb` | `tools/blender/make_props.py` | ถุงใส 3 ชั้น + น้ำ + ยางรัด |
| `models/warehouse.glb` | `tools/blender/make_props.py` | คลังสินค้าสัตว์มีชีวิต (ใช้ทั้ง NRT และ BKK) |
| `models/xray.glb` | `tools/blender/make_props.py` | เครื่อง X-ray สายพาน |
| `models/pond.glb` | `tools/blender/make_scenery.py` | บ่อปลาขอบหิน |
| `models/dolly.glb` | `tools/blender/make_scenery.py` | แท่นลากสินค้าในสนามบิน |
| `models/farmhouse.glb` | `tools/blender/make_scenery.py` | บ้านฟาร์มแบบญี่ปุ่น (ฟาร์มผู้ส่งและฟาร์มบริษัท) |
| `models/dof.glb` | `tools/blender/make_scenery.py` | อาคารด่านตรวจและกักกัน (ป้ายภาษาอังกฤษทั่วไป ไม่ใช่ตราหน่วยงานจริง) |
| `models/trees.glb` | `tools/blender/make_scenery.py` | ต้นไม้ 2 แบบ |
| `models/reefer.glb` | `tools/blender/make_reefer.py` | รถบรรทุกห้องเย็น (ไม่ระบุตัวเลขอุณหภูมิตามข้อตกลงของทีม) |
| `models/japan.glb` | `tools/blender/make_culture.py` | บรรยากาศญี่ปุ่น: โทริอิ โคมหิน ซากุระ สน ฟูจิ รั้วไผ่ |
| `models/thai.glb` | `tools/blender/make_culture.py` | บรรยากาศไทย: ศาลพระภูมิ ศาลาทรงไทย มะพร้าว กล้วย เจดีย์ เรือนไทย |

แผนที่ในขั้น 9: Natural Earth 1:50m Admin 0 Countries (สาธารณสมบัติ) ตัดและย่อด้วย `tools/build-map.mjs` → `map/asia.json`

โลโก้ที่หางเครื่องบิน: โลโก้สาขา Aviation Safety Management มหาวิทยาลัยศรีปทุม (`textures/aviation-logo.webp`) มาร์ชเป็นผู้ให้มาใช้ในงานนี้

เปิดดูโมเดลทั้งหมดใน Blender: รัน `tools/blender/make_showcase.py` จะได้ไฟล์ `assets/koi-models.blend` (ไม่เก็บลง git)

ภาพตัวอย่างของแต่ละโมเดลอยู่ใน `previews/` สร้างใหม่ได้ด้วยคำสั่ง (แล้วรัน `npm run inline` เพื่อฝังลงไฟล์เว็บ):

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python tools/blender/make_airliner.py
```

ไฟล์เครื่องบิน `CartoonPlane.zip` (CC0) ที่โหลดมาก่อนหน้า ไม่ได้ใช้ เพราะเป็นเครื่องบินใบพัดลำเล็ก ไม่ใช่เครื่องบินลำตัวกว้าง
