import nuke
import os
import sys

EXTENTIONS = [".exr", ".jpg", ".tga", ".png"]

def get_all_valid_files(input_footage_folder):
    """returns start and end frames of sequence"""
    for seq in nuke.getFileNameList(input_footage_folder):
        if any(ext in seq for ext in EXTENTIONS):
            
            return os.path.join(input_footage_folder, seq).replace("\\", "/")
    


def setup_read_node(input_footage_folder):
    
    """setup read node"""
    
    valid_files = get_all_valid_files(input_footage_folder)

    read_node = nuke.toNode("INPUT_IMAGE")
    read_node.knob("file").fromUserText(valid_files)

def unique_channel_layer_list(nodeToProcess):
    rawChannelList = nodeToProcess.channels()
    channelLayerList = []
    for channel in rawChannelList:
        channelLayer = channel.split('.')
        channelLayerList.append(channelLayer[0])
    return list(set(channelLayerList))

def setup_renders_read_nodes(renders_folder):
    lighting_dir = os.path.join(renders_folder, "lighting")
    if not os.path.exists(lighting_dir):
        return

    renders_list = os.listdir(lighting_dir)
    if not renders_list:
        return
    shuffle_x_pos = 50
    shuffle_y_pos = 500

    read_x_pos = 1000
    for each_render in renders_list:
        render_path = os.path.join(lighting_dir, each_render)
        valid_files = get_all_valid_files(render_path)
        read_node_name = f"{each_render}_Input"
        read_node = nuke.createNode("Read")

        layer_contact_node = nuke.createNode("LayerContactSheet")
        layer_contact_node.setInput(0,read_node)
        layer_contact_node.setXYpos(read_x_pos+200, 30)

        read_node["name"].setValue(read_node_name)
        read_node.knob("file").fromUserText(valid_files)
        read_node.setXYpos(read_x_pos, 0)
        unique_channel_layers = unique_channel_layer_list(read_node)

        read_x_pos += 2000

        for channel_layer in unique_channel_layers:
            shuffle_node = nuke.nodes.Shuffle(name='Shuffle_' + channel_layer)
            shuffle_node.knob('in').setValue(channel_layer)
            shuffle_node.setInput(0,read_node)
            shuffle_node.setXYpos(shuffle_x_pos, shuffle_y_pos)
            shuffle_x_pos += 200
            shuffle_y_pos += 0
            
    

def main():
    template_path = sys.argv[1]

    input_footage_folder = sys.argv[2]
    
    script_folder = sys.argv[3]
    
    shot_name = sys.argv[4]
    
    renders_folder = sys.argv[5]
    
    print(f"render folder : {renders_folder}")

    print(f"Opening template: {template_path}")

    nuke.scriptOpen(template_path)
    
    setup_read_node(input_footage_folder)
    
    setup_renders_read_nodes(renders_folder)

    out_path = os.path.join(script_folder, f"{shot_name}_v001.nk")
    
    print(f"Saving to: {out_path}")
    nuke.scriptSave(out_path)

main()