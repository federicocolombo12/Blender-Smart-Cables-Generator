bl_info = {
    "name": "Smart Cable Generator",
    "author": "Federico Colombo",
    "version": (2, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Tech Art",
    "description": "Generates parametric hanging cables between selected vertices across multiple objects",
    "category": "3D View",
}

import bpy
import bmesh
import random

def update_preset(self, context):
    if self.preset == 'POWER':
        self.thickness = 0.1
        self.gravity = 0.1
        self.resolution = 16
        self.cable_count = 1
    elif self.preset == 'WIRE':
        self.thickness = 0.01
        self.gravity = 0.02
        self.resolution = 8
        self.cable_count = 1
    elif self.preset == 'VINE':
        self.thickness = 0.04
        self.gravity = 0.4
        self.resolution = 24
        self.cable_count = 1
    elif self.preset == 'BUNDLE':
        self.thickness = 0.02
        self.gravity = 0.15
        self.resolution = 16
        self.cable_count = 5
        self.bundle_spread = 0.2

class SmartCableProperties(bpy.types.PropertyGroup):
    thickness: bpy.props.FloatProperty(name="Thickness", default=0.05, min=0.001, max=1.0)
    gravity: bpy.props.FloatProperty(name="Gravity Sag", default=0.15, min=0.0, max=2.0)
    resolution: bpy.props.IntProperty(name="Resolution", default=16, min=3, max=100)
    
    cable_count: bpy.props.IntProperty(name="Cable Count", default=1, min=1, max=20, description="Generates a bundle of cables")
    bundle_spread: bpy.props.FloatProperty(name="Bundle Spread", default=0.1, min=0.0, max=2.0, description="Random offset for bundled cables")
    convert_to_mesh: bpy.props.BoolProperty(name="Auto-Convert to Mesh", default=False, description="Instantly converts the curve to a game-ready polygon mesh for FBX export")

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
            ('BUNDLE', "Messy Wire Bundle", ""),
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
        distance = (p1 - p2).length
        
        generated_cables = []
        
        for c in range(props.cable_count):
            curve_data = bpy.data.curves.new(name='SmartCable_Curve', type='CURVE')
            curve_data.dimensions = '3D'
            curve_data.bevel_depth = props.thickness
            curve_data.bevel_resolution = 4
            
            if props.material:
                curve_data.materials.append(props.material)
            
            spline = curve_data.splines.new('POLY')
            spline.points.add(props.resolution - 1)
            
            for i in range(props.resolution):
                t = i / (props.resolution - 1)
                
                x = p1.x * (1 - t) + p2.x * t
                y = p1.y * (1 - t) + p2.y * t
                z = p1.z * (1 - t) + p2.z * t
                
                # Bundle variation math
                if props.cable_count > 1:
                    offset_factor = 4.0 * t * (1.0 - t)
                    x += (random.random() - 0.5) * props.bundle_spread * offset_factor
                    y += (random.random() - 0.5) * props.bundle_spread * offset_factor
                    gravity_var = props.gravity * random.uniform(0.8, 1.2)
                else:
                    gravity_var = props.gravity
                
                sag = gravity_var * distance * 4.0 * t * (1.0 - t)
                z -= sag
                
                spline.points[i].co = (x, y, z, 1.0)
                
            cable_obj = bpy.data.objects.new('SmartCable', curve_data)
            bpy.context.collection.objects.link(cable_obj)
            generated_cables.append(cable_obj)
        
        for obj, bm, v in selected_verts_refs:
            v.select = False
            bmesh.update_edit_mesh(obj.data)
            
        if props.convert_to_mesh:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            for cable in generated_cables:
                cable.select_set(True)
                context.view_layer.objects.active = cable
            bpy.ops.object.convert(target='MESH')
            self.report({'INFO'}, f"Generati {props.cable_count} cavi e convertiti in Mesh Game-Ready!")
        else:
            self.report({'INFO'}, f"Generati {props.cable_count} cavi con successo!")
            
        return {'FINISHED'}

class VIEW3D_PT_SmartCable(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tech Art'
    bl_label = "Smart Cable Gen 2.0"

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
        layout.label(text="Advanced Settings:")
        layout.prop(props, "cable_count")
        if props.cable_count > 1:
            layout.prop(props, "bundle_spread")
            
        layout.separator()
        layout.prop(props, "material")
        layout.prop(props, "convert_to_mesh", icon='MESH_DATA')
        
        layout.separator()
        layout.operator("object.generate_smart_cable", text="Generate Cable(s)", icon='OUTLINER_OB_CURVE')

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
