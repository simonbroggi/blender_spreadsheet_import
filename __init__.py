bl_info = {
    "name": "Generig JSON Importer",
    "author": "Simon Broggi",
    "version": (0,1,0),
    "blender": (3, 3, 0),
    "location": "File > Import-Export",
    "description": "Import data from JSON file for use with geometry nodes",
    "category": "Import-Export",
}

from email.policy import default
from pydoc import describe
import bpy
import json

def read_json_data(context, filepath, data_array_name):
    print("importing data from json...")
    f = open(filepath, 'r', encoding='utf-8-sig')
    data = json.load(f)
    
    data_array = data[data_array_name]
    
    # name of the object and mesh
    data_name = "imported_data"
    
    mesh = bpy.data.meshes.new(name=data_name)
    mesh.vertices.add(len(data_array))
    #coordinates = np.ones((len(data_array)*3))
    #mesh.vertices.foreach_set("co", coordinates)
    
    # add custom data
    mesh.attributes.new(name='weiblich', type='BOOLEAN', domain='POINT')
    mesh.attributes.new(name='kanton', type='INT', domain='POINT')

    # set data according to json
    i=0
    for k in data_array:
        mesh.attributes['weiblich'].data[i].value = k['geschlecht'] == 'F'
        mesh.attributes['kanton'].data[i].value = k['kanton_nummer']
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


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

# https://blender.stackexchange.com/questions/16511/how-can-i-store-and-retrieve-a-custom-list-in-a-blend-file
# https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute
# https://docs.blender.org/api/master/bpy_types_enum_items/attribute_domain_items.html?highlight=mesh+attributes

class DataFieldPropertiesGroup(bpy.types.PropertyGroup):
    fieldName : StringProperty(
        name="Field name",
        description="The name of the field to import",
        default="",
    )
    fieldDataType: EnumProperty(
        name="Data Type Enum",
        description="Choose Data Type",
        items=(
            ('FLOAT', "Float", "Floating-point value"),
            ('INT', "Integer", "32-bit integer"),
            ('BOOLEAN', "Boolean", "True or false"),
        ),
        default='FLOAT',
    )

class ImportJsonData(Operator, ImportHelper):
    """Import data from JSON files"""
    bl_idname = "import.json"  # important since its how bpy.ops.import.json is constructed
    bl_label = "Import JSON Data"

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    array_name: StringProperty(
        name="Array name",
        description="The name of the array to import",
        default="",
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    field_names: bpy.props.CollectionProperty(
        type=DataFieldPropertiesGroup,
        name="Field names",
        description="All the fields that should be imported",
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        return read_json_data(context, self.filepath, self.array_name)

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
    DataFieldPropertiesGroup,
    ImportJsonData,
    VIEW3D_PT_import_json,
    JSON_PT_imort_options,
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

