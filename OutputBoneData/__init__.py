bl_info = {
    "name" : "OutputBoneData",
    "author" : "Jonas",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Animation"
}
from bl_ui.space_toolsystem_common import item_from_id
import bpy 
import json
import math
import os

from bpy import types

class Output_OT_Data(bpy.types.Operator):
    bl_idname="ops.outputdata"
    bl_label="Output Data"
    
    @classmethod
    def poll(cls, context):     
        return bpy.context.object != "" 

    def execute(self, context): 

        
        obj = bpy.context.object
        scn = bpy.context.scene
        js = scn.Json

        ebones = obj.pose.bones
        
        if bpy.context.object.mode!='POSE':
            bpy.ops.object.mode_set(mode='POSE') 

        def check_bool(ax):
            if ax:
                return 1
            else :
                return 0
        
        if js.Jenum == 'OP1':
            js.Junit = 1
        elif js.Jenum == 'OP2':
            js.Junit = 100
        elif js.Jenum == 'OP3':
            js.Junit = 10000

        ## bone types
        cr = {}
        cl = {}
        tr = {}
        dt = {}
        # constraints types
        ccr = []
        ccl = []
        ttr = []
        ddt = []
        # json data
        cons = {}
   
        for i in ebones:
            if i.constraints != None :
                for j in i.constraints:        
                    if j.type == 'COPY_ROTATION': 
                  
                        cr[i.name] = {'BoneName':i.name,'Tgbone':j.subtarget,
                        'Axis':[check_bool(j.use_x),check_bool(j.use_y),check_bool(j.use_z)],
                        'Invert':[check_bool(j.invert_x),check_bool(j.invert_y),check_bool(j.invert_z)],
                        'Mix':j.mix_mode,
                        'Influence':j.influence
                        }  
                        ccr.append(cr[i.name]) 
                        
                    if j.type == 'COPY_LOCATION': 
                           
                        cl[i.name] = {'BoneName':i.name,'Tgbone':j.subtarget,
                        'Axis':[check_bool(j.use_x),check_bool(j.use_y),check_bool(j.use_z)],
                        'Invert':[check_bool(j.invert_x),check_bool(j.invert_y),check_bool(j.invert_z)],
                        'Mix':j.mix_mode,
                        'Influence':j.influence
                        }           
                        ccl.append(cl[i.name])

                    if j.type == 'TRANSFORM': 
                        
                        fromx = []
                        fromy = []
                        fromz = []
                        if j.map_from == 'LOCATION':
                            fromx = [j.from_min_x*js.Junit,j.from_max_x*js.Junit]
                            fromy = [j.from_min_y*js.Junit,j.from_max_y*js.Junit]
                            fromz = [j.from_min_z*js.Junit,j.from_max_z*js.Junit]

                        elif j.map_from == 'ROTATION':
                            fromx = [round(math.degrees(j.from_min_x_rot)),round(math.degrees(j.from_max_x_rot))]
                            fromy = [round(math.degrees(j.from_min_y_rot)),round(math.degrees(j.from_max_y_rot))]
                            fromz = [round(math.degrees(j.from_min_z_rot)),round(math.degrees(j.from_max_z_rot))]

                        elif j.map_from == 'SCALE':
                            fromx = [j.from_min_x_scale,j.from_max_x_scale]
                            fromy = [j.from_min_y_scale,j.from_max_y_scale]
                            fromz = [j.from_min_z_scale,j.from_max_z_scale]

                        tox = []
                        toy = []
                        toz = []
                        if j.map_to == 'LOCATION':
                            tox = [j.to_min_x*js.Junit,j.to_max_x/js.Junit]
                            toy = [j.to_min_y*js.Junit,j.to_max_y/js.Junit]
                            toz = [j.to_min_z*js.Junit,j.to_max_z/js.Junit]

                        elif j.map_to == 'ROTATION':
                            tox = [round(math.degrees(j.to_min_x_rot)),round(math.degrees(j.to_max_x_rot))]
                            toy = [round(math.degrees(j.to_min_y_rot)),round(math.degrees(j.to_max_y_rot))]
                            toz = [round(math.degrees(j.to_min_z_rot)),round(math.degrees(j.to_max_z_rot))]

                        elif j.map_to == 'SCALE':
                            tox = [j.to_min_x_scale,j.to_max_x_scale]
                            toy = [j.to_min_y_scale,j.to_max_y_scale]
                            toz = [j.to_min_z_scale,j.to_max_z_scale]


                        tr[i.name] = {'ConsName':j.name,'BoneName':i.name,'Tgbone':j.subtarget,
                        'Traget':j.target_space,'Owner':j.owner_space,
                        'Influence':j.influence,
                        'MapFrom':j.map_from,
                        #'MapFromMode':j.from_rotation_mode,
                        'MapFromX':fromx,
                        'MapFromY':fromy,
                        'MapFromZ':fromz,
                        'MapTO':j.map_to,
                        #'Order':j.to_euler_order,
                        'Xaxis':j.map_to_x_from,'MapToX':tox,
                        'Yaxis':j.map_to_y_from,'MapToY':toy,
                        'Zaxis':j.map_to_z_from,'MapToZ':toz,
                        'Mix':j.mix_mode_rot
                        }
                        ttr.append(tr[i.name])

                    if j.type == 'DAMPED_TRACK':
                        dt[i.name] = {'BoneName':i.name,'Tgbone':j.subtarget,
                        'Trackaxis': j.track_axis,'Influence':j.influence
                        }
                        ddt.append(dt[i.name])

        cons = {'COPY_ROTATION':ccr,'COPY_LOCATION':ccl,'TRANSFORM':ttr,'DAMPED_TRACK':ddt}
        data = json.dumps(cons, indent=1, ensure_ascii=True)

        
        save_path = js.Jpath
        file_name = os.path.join(save_path, js.Jname + '.json')

        with open(file_name, 'w') as outfile:
            outfile.write(data + '\n')
            outfile.close()

        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({"INFO"}, "List successed!")
        
        return {"FINISHED"}

        
class Data_PT_Panel(bpy.types.Panel):   

    bl_idname = 'data_pt_panel'        
    bl_label = "Output Bone'Data"              
    bl_space_type = "VIEW_3D"           
    bl_region_type = "UI"               
    bl_category = "OutData"          

    def draw(self,context):             
        
        layout = self.layout  
        obj = bpy.context.object
        scn = bpy.context.scene
        js = scn.Json

        if context.object != None and context.object.type == 'ARMATURE':

            row = layout.row(align=True)    
            row.label(text="骨架:      " + obj.name)

            row = layout.row()  
            row.prop(js,'Jname',text="名称")

            row = layout.row()  
            row.prop(js,'Jpath',text="路径")

            row = layout.row()              
            row.operator("ops.outputdata", text="Export") 

        else:
            layout.label(text='请选择一副骨架对象！', icon='ERROR')
            
            
class Unit_PT_Panel(bpy.types.Panel):
    
    bl_idname = "unit_pt_panel"
    bl_label = "Unit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OutData"
    bl_parent_id = "data_pt_panel"
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self,context):             
        
        layout = self.layout  
        scn = bpy.context.scene
        js = scn.Json

        row = layout.row()              
        row.prop(js,'Jenum',text="单位") 

class Json_PO_Data(bpy.types.PropertyGroup):

    Jname : bpy.props.StringProperty \
        (      
            name = "Json'name",
            default = "",
            description = "json file's name"  
        ) 

    Jpath : bpy.props.StringProperty \
        (
            name = "Json'path",
            default = "",
            description = "Define the json path of the project",
            subtype = 'DIR_PATH'
        )
    Jenum : bpy.props.EnumProperty \
        (
            name = "请选择单位大小",
            default = 'OP1',
            items=[
                ('OP1','米(M)',''),
                ('OP2','厘米(CM)',''),
                ('OP3','毫米(MM)','')         
            ]
        )
    Junit : bpy.props.IntProperty(default = 1)


classes = (

    Json_PO_Data,
    Output_OT_Data,
    Data_PT_Panel,
    Unit_PT_Panel
    
)
def register():   
    for cls in classes:
        bpy.utils.register_class(cls) 
        bpy.types.Scene.Json = bpy.props.PointerProperty(type = Json_PO_Data)

        # bpy.types.Scene.Jname = bpy.props.StringProperty \
        # (      
        #     name = "Json'name",
        #     default = "",
        #     description = "json file's name"  
        # )     
        # bpy.types.Scene.Jpath = bpy.props.StringProperty \
        # (
        #     name = "Json'path",
        #     default = "",
        #     description = "Define the json path of the project",
        #     subtype = 'DIR_PATH'
        # )
        # bpy.types.Scene.Unit = bpy.props.IntProperty \
        # (
        #     default = 1, 
        # )
           
def unregister():         
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.Json

        # del bpy.types.Scene.Jname
        # del bpy.types.Scene.Jpath
        # del bpy.types.Scene.Unit
        

if __name__ == '__main__': 
    register()