# ถ่ายภาพตรวจงานจาก Blender ที่เปิดอยู่ (ผ่าน MCP) โดยไม่ทิ้งของในฉาก
# ใช้: snap(path, cam_loc, target, lens) — ใส่ไฟแดด/กล้อง/พื้นชั่วคราว เรนเดอร์ แล้วลบออก
import bpy, math


def snap(path, cam_loc, target=(0, 0, 0), lens=50, size=(960, 540), ground=True):
    sc = bpy.context.scene
    temp = []
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except Exception:
        sc.render.engine = 'BLENDER_WORKBENCH'
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    if sc.world is None:
        sc.world = bpy.data.worlds.new('snap_world')
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.62, 0.78, 0.92, 1); bg.inputs['Strength'].default_value = 0.9
    sun = bpy.data.lights.new('snap_sun', 'SUN'); sun.energy = 3.5
    so = bpy.data.objects.new('snap_sun', sun); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    sc.collection.objects.link(so); temp.append(so)
    if ground:
        me = bpy.data.meshes.new('snap_ground')
        s = 200
        me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
        g = bpy.data.objects.new('snap_ground', me); sc.collection.objects.link(g); temp.append(g)
        gm = bpy.data.materials.new('snap_ground_mat'); gm.diffuse_color = (0.6, 0.62, 0.64, 1)
        gm.use_nodes = True
        gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.6, 0.62, 0.64, 1)
        me.materials.append(gm)
    cam = bpy.data.cameras.new('snap_cam'); cam.lens = lens
    co = bpy.data.objects.new('snap_cam', cam); co.location = cam_loc; sc.collection.objects.link(co); temp.append(co)
    tgt = bpy.data.objects.new('snap_tgt', None); tgt.location = target; sc.collection.objects.link(tgt); temp.append(tgt)
    c = co.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    old_cam = sc.camera
    sc.camera = co
    sc.render.filepath = path
    try:
        bpy.ops.render.render(write_still=True)
    finally:
        sc.camera = old_cam
        for ob in temp:
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data is not None and data.users == 0:
                for coll in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
                    if data.name in coll and coll[data.name] == data:
                        coll.remove(data)
                        break
        for m in list(bpy.data.materials):
            if m.name.startswith('snap_') and m.users == 0:
                bpy.data.materials.remove(m)
    return path
