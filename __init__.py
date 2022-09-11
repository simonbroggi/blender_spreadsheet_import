bl_info = {
    "name": "Generig JSON Importer",
    "author": "Simon Broggi",
    "version": (0,1,0),
    "blender": (3, 3, 0),
    "location": "File > Import-Export",
    "description": "Import data from JSON file for use with geometry nodes",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
import json
import random #todo: remove

def read_json_data(context, filepath, data_array_name, field_names):
    print("importing data from json...")
    f = open(filepath, 'r', encoding='utf-8-sig')
    data = json.load(f)
    
    #todo: doain per data array.
    data_array = data[data_array_name] 
    
    # name of the object and mesh
    data_name = "imported_data"
    
    mesh = bpy.data.meshes.new(name=data_name)
    mesh.vertices.add(len(data_array))
    #coordinates = np.ones((len(data_array)*3))
    #mesh.vertices.foreach_set("co", coordinates)
    
    # https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute

    # add custom data
    for field_name in field_names:
        mesh.attributes.new(name=field_name.name, type=field_name.dataType, domain='POINT')
    # mesh.attributes.new(name='weiblich', type='BOOLEAN', domain='POINT')
    # mesh.attributes.new(name='kanton', type='INT', domain='POINT')

    # set data according to json
    i=0
    for k in data_array:
        for field_name in field_names:
            mesh.attributes[field_name.name].data[i].value = k[field_name.name]
        #mesh.attributes['weiblich'].data[i].value = k['geschlecht'] == 'F'
        #mesh.attributes['kanton'].data[i].value = k['kanton_nummer']
        mesh.vertices[i].co = (i,0.0,0.0) # set vertex x position according to index
        i=i+1
    
    # Create new object
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    obj = bpy.data.objects.new(data_name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    mesh.update()
    mesh.validate()
    
    f.close()
    return {'FINISHED'}


class MY_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'
        #item is a DataFieldPropertiesGroup
        #print(type(item.name))
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            #layout.label(text=item.name, icon = custom_icon)
            layout.prop(data=item, property="name")
            layout.prop(data=item, property="dataType")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            #layout.label(text="", icon = custom_icon)
            layout.prop(data=item, property="name")
            layout.prop(data=item, property="dataType")


# https://blender.stackexchange.com/questions/16511/how-can-i-store-and-retrieve-a-custom-list-in-a-blend-file
# https://docs.blender.org/api/master/bpy_types_enum_items/attribute_domain_items.html?highlight=mesh+attributes

class DataFieldPropertiesGroup(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(
        name="Field Name",
        description="The name of the field to import",
        default="",
    )

    #  https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute
    dataType: bpy.props.EnumProperty(
        name="Field Data Type",
        description="Choose Data Type",
        items=(
            ('FLOAT', "Float", "Floating-point value"),
            ('INT', "Integer", "32-bit integer"),
            ('BOOLEAN', "Boolean", "True or false"),
            ('STRING', "String", "Text string"),
        ),
        default='FLOAT',
    )

# ImportHelper is a helper class, defines filename and invoke() function which calls the file selector.
class ImportJsonData(bpy.types.Operator, ImportHelper):
    """Import data from JSON files"""
    bl_idname = "import.json"  # important since its how bpy.ops.import.json is constructed
    bl_label = "Import JSON Data"

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    array_name: bpy.props.StringProperty(
        name="Array name",
        description="The name of the array to import",
        default="",
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: bpy.props.BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    field_names: bpy.props.CollectionProperty(
        type=DataFieldPropertiesGroup,
        name="Field names",
        description="All the fields that should be imported",
    )

    field_name_index: bpy.props.IntProperty(
        name="Index of field_names",
        default=0,
    )

    type: bpy.props.EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        return read_json_data(context, self.filepath, self.array_name, self.field_names)

class IMPORT_OT_filed_add(bpy.types.Operator):
    bl_idname = "import.json_field_add"
    bl_label = "Add field"

    def execute(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        item = operator.field_names.add()

        operator.field_name_index = len(operator.field_names) - 1

        #todo: dont initialize randomly
        item.name = random.sample(("foo", "bar", "asdf"), 1)[0]
        item.dataType = 'INT' if random.random() > 0.5 else 'BOOLEAN'
        
        return {'FINISHED'}

class IMPORT_OT_field_remove(bpy.types.Operator):
    bl_idname = "import.json_field_remove"
    bl_label = "Remove field"

    def execute(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        index = operator.field_name_index
        operator.field_names.remove(index)
        operator.field_name_index = min(max(0,index - 1), len(operator.field_names)-1)
        return {'FINISHED'}


class JSON_PT_imort_options(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Dataa Import Options"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "IMPORT_OT_json"

    def draw(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        layout = self.layout

        #layout.template_list("UI_UL_list", "", operator, "field_names", operator, )
        
        # success with this tutorial!
        # https://sinestesia.co/blog/tutorials/using-uilists-in-blender/

        rows = 2
        filed_names_exist = bool(len(operator.field_names) >= 1)
        if filed_names_exist:
            rows = 4

        row = layout.row()
        row.template_list("MY_UL_List", "", operator, "field_names", operator, "field_name_index", rows=rows)

        col = row.column(align=True)
        col.operator(IMPORT_OT_filed_add.bl_idname, icon='ADD', text="")
        col.operator(IMPORT_OT_field_remove.bl_idname, icon='REMOVE', text="")

        # print(operator.field_names)
        pass

class VIEW3D_PT_import_json(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Import Json"
    bl_label = "labllle"

    def draw(self, context):
        self.layout.operator(ImportJsonData.bl_idname, text="JSON Import Operator")
        

blender_classes = [
    MY_UL_List,
    DataFieldPropertiesGroup,
    ImportJsonData,
    VIEW3D_PT_import_json,
    JSON_PT_imort_options,
    IMPORT_OT_filed_add,
    IMPORT_OT_field_remove,
]

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportJsonData.bl_idname, text="JSON Import Operator")

# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access)
def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

