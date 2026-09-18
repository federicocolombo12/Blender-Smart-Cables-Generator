bl_info = {
    "name": "Smart Cable Generator",
    "author": "Federico Colombo",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Tech Art",
    "description": "Generates parametric hanging cables between selected vertices across multiple objects",
    "category": "3D View",
}

import bpy
import bmesh

def update_preset(self, context):
    if self.preset == 'POWER':
        self.thickness = 0.1
        self.gravity = 0.1
        self.resolution = 16
    elif self.preset == 'WIRE':
        self.thickness = 0.01
        self.gravity = 0.02
        self.resolution = 8
    elif self.preset == 'VINE':
        self.thickness = 0.04
        self.gravity = 0.4
        self.resolution = 24

class SmartCableProperties(bpy.types.PropertyGroup):
    thickness: bpy.props.FloatProperty(name="Thickness", default=0.05, min=0.001, max=1.0)
    gravity: bpy.props.FloatProperty(name="Gravity Sag", default=0.15, min=0.0, max=2.0)
    resolution: bpy.props.IntProperty(name="Resolution", default=16, min=3, max=100)
    material: bpy.props.PointerProperty(
        name="Material",
        type=bpy.types.Material,
        description="Material to assign to the generated cable"
    )
    preset: bpy.props.EnumProperty(
        name="Preset",
        items=[
            ('CUSTOM', "Custom", ""),
            ('POWER', "Thick Power Cable", ""),
            ('WIRE', "Thin Wire", ""),
            ('VINE', "Droopy Vine", ""),
        ],
        update=update_preset
    )

class OBJECT_OT_GenerateCable(bpy.types.Operator):
    bl_idname = "object.generate_smart_cable"
    bl_label = "Generate Cable"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        props = context.scene.smart_cable_props
        
        selected_global_coords = []
        selected_verts_refs = []
        
        for obj in context.objects_in_mode:
            if obj.type == 'MESH':
                bm = bmesh.from_edit_mesh(obj.data)
                bm.verts.ensure_lookup_table()
                
                matrix = obj.matrix_world
                for v in bm.verts:
                    if v.select:
                        selected_global_coords.append(matrix @ v.co.copy())
                        selected_verts_refs.append((obj, bm, v))
        
        if len(selected_global_coords) != 2:
            self.report({'ERROR'}, f"Selezionati {len(selected_global_coords)} vertici. Scegline esattamente 2!")
            return {'CANCELLED'}

        p1 = selected_global_coords[0]
        p2 = selected_global_coords[1]
        
        curve_data = bpy.data.curves.new(name='SmartCable_Curve', type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = props.thickness
        curve_data.bevel_resolution = 4
        
        if props.material:
            curve_data.materials.append(props.material)
        
        spline = curve_data.splines.new('POLY')
        spline.points.add(props.resolution - 1)
        
        distance = (p1 - p2).length
        
        for i in range(props.resolution):
            t = i / (props.resolution - 1)
            x = p1.x * (1 - t) + p2.x * t
            y = p1.y * (1 - t) + p2.y * t
            z = p1.z * (1 - t) + p2.z * t
            
            sag = props.gravity * distance * 4.0 * t * (1.0 - t)
            z -= sag
            
            spline.points[i].co = (x, y, z, 1.0)
            
        cable_obj = bpy.data.objects.new('SmartCable', curve_data)
        bpy.context.collection.objects.link(cable_obj)
        
        for obj, bm, v in selected_verts_refs:
            v.select = False
            bmesh.update_edit_mesh(obj.data)
        
        self.report({'INFO'}, "Cavo generato con successo!")
        return {'FINISHED'}

class VIEW3D_PT_SmartCable(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tech Art'
    bl_label = "Smart Cable Gen"

    def draw(self, context):
        layout = self.layout
        props = context.scene.smart_cable_props
        
        layout.prop(props, "preset")
        
        col = layout.column()
        col.enabled = (props.preset == 'CUSTOM')
        col.prop(props, "thickness")
        col.prop(props, "gravity")
        col.prop(props, "resolution")
        
        layout.separator()
        layout.prop(props, "material")
        layout.separator()
        layout.operator("object.generate_smart_cable", text="Generate Cable", icon='OUTLINER_OB_CURVE')

classes = (
    SmartCableProperties,
    OBJECT_OT_GenerateCable,
    VIEW3D_PT_SmartCable,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.smart_cable_props = bpy.props.PointerProperty(type=SmartCableProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.smart_cable_props

if __name__ == "__main__":
    register()
