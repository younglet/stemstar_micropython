import requests


BASE_URL = 'http://192.168.19.28'

download_url = BASE_URL + '/download'
scan_url = BASE_URL + '/scan/'

def scan_directory(directory):
    response = requests.get(scan_url + directory)
    return response.json()


def download_file(file_path):
    response = requests.post(download_url, json={
        'file_path': file_path
    })
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"<{file_path}> downloaded successfully.")
    else:
        print(f"Failed to download file: {response.status_code} - {response.text}")
        
        
if __name__ == '__main__':
    folder = 'lib'
    items = scan_directory(folder)
    import os
    
    for i, item in enumerate(items):
        print(f"{item['name']:<40} {i+1:0>2}/{len(items):0>2}")
        if item['is_directory']:
            try:
                os.stat(item['name'])
            except OSError:
                os.mkdir(item['name'])
        for file in item['files']: 
            print(f'/t{file["name"]:<20} {i+1:0>2}/{len(items):0>2}')
            download_file(file['path'])
            