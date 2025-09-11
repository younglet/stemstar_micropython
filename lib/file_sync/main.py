
# TODO：添加文件大小字段
# TODO:针对文件大小检测，进行分块甚至是逐行传输


from microdot import Microdot, send_file
import os
import json

def scan_directory(dir_path):
    try:
        stat_info = os.stat(dir_path)
        if not (stat_info[0] & 0x4000): 
            print(f"Error: '{dir_path}' is not a directory.")
            return "[]"
    except OSError:
        print(f"Error: Directory '{dir_path}' does not exist or cannot be accessed.")
        return "[]"

    abs_dir_path = dir_path
    result = []
    
    try:
        entries = os.listdir(dir_path)
    except OSError as e:
        print(f"Error reading directory '{dir_path}': {e}")
        return "[]"

    for entry in entries:
        entry_path = dir_path + '/' + entry 
        
        try:
            entry_stat = os.stat(entry_path)
        except OSError:
            print(f"Warning: Cannot stat '{entry_path}'. Skipping.")
            continue

        is_dir = bool(entry_stat[0] & 0x4000) # 检查是否为目录

        if not is_dir: 
            # 处理文件：提取项目名（去掉扩展名）
            last_dot_index = entry.rfind('.')
            if last_dot_index > 0: 
                project_name = entry[:last_dot_index]
            else:
                project_name = entry 

            file_info = {
                'name': entry,
                'path': entry_path
            }
            # 将整个项目信息构造成一个字典，包含 name, file_count, is_directory, files
            result.append({
                'name': project_name,          # 项目名（无扩展名）
                'file_count': 1,
                'is_directory': False,
                'files': [file_info]
            })

        else:  
            # 处理目录
            subdir_files = []
            try:
                sub_entries = os.listdir(entry_path)
            except OSError as e:
                print(f"Error reading subdirectory '{entry_path}': {e}")
                continue

            for sub_entry in sub_entries:
                sub_entry_path = entry_path + '/' + sub_entry
                try:
                    sub_entry_stat = os.stat(sub_entry_path)
                    if not (sub_entry_stat[0] & 0x4000): # 是文件
                        subdir_files.append({
                            'name': sub_entry,
                            'path': sub_entry_path
                        })
                except OSError:
                    print(f"Warning: Cannot stat '{sub_entry_path}'. Skipping.")
                    continue

            # 将整个目录项目信息构造成一个字典
            result.append({
                'name': entry,                 # 目录名保持不变
                'file_count': len(subdir_files),
                'is_directory': True, 
                'files': subdir_files
            })

    # 将结果列表转换为JSON字符串
    try:
        return json.dumps(result, indent=2)
    except TypeError:
        return json.dumps(result)


    
app = Microdot()


@app.get('/scan/<dir_path>')
def handle_scan(req, dir_path):
    dir_path = dir_path.replace('_', '/')
    json_data = scan_directory(dir_path)
    return json_data

@app.post('/download')
def handle_download(req):
    file_path = os.path.join(os.getcwd(), req.json.get('file_path', ''))
    if not os.path.exists(file_path):
        return 'File not found', 404
    return send_file(file_path)


app.run(port='80')