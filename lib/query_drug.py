import usocket
import json

def http_post(host, path, headers, body=None):
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    try:
        addr_info = usocket.getaddrinfo(host, 80)
        addr = addr_info[0][4]
        sock.connect(addr)
        if body is None:
            body = ''
        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        for k, v in headers.items():
            request += f"{k}: {v}\r\n"
        request += "Connection: close\r\n"
        request += f"Content-Length: {len(body)}\r\n"
        request += "\r\n"
        request += body
        
        sock.send(request.encode('utf-8'))
        response = b''
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk
        sock.close()
        
        header_body = response.split(b'\r\n\r\n', 1)
        if len(header_body) < 2:
            raise ValueError("No body in response")
        
        header, body = header_body
        if b'Transfer-Encoding: chunked' in header or b'transfer-encoding: chunked' in header:
            return parse_chunked_body(body)
        else:
            return body.decode('utf-8')
    
    finally:
        sock.close()

def parse_chunked_body(body_data):
    """解析 chunked 编码的 body"""
    body_str = body_data.decode('utf-8')
    full_body = ''
    lines = body_str.split('\r\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        try:
            chunk_size = int(line, 16)
        except ValueError:
            raise ValueError(f"Invalid chunk size: {line}")
        if chunk_size == 0:
            break  
        i += 1
        if i >= len(lines):
            break
        chunk_data = lines[i]
        if len(chunk_data) >= chunk_size:
            full_body += chunk_data[:chunk_size]
        else:
            full_body += chunk_data
        i += 1
    
    return full_body


def query_drug(code):
    APPCODE = 'b4f58e2b4aba4b2c9a1eb9667df7ac04'
    host = 'gwgp-w8ah4tjhazs.n.bdcloudapi.com'
    path = f'/v4/drug_shape_code/query?code={code}'
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'X-Bce-Signature': f'AppCode/{APPCODE}'
    }
    
    try:
        raw_body = http_post(host, path, headers, '{}')
        data = json.loads(raw_body)
        print("✅ JSON 解析成功")
        return data
    except Exception as e:
        print("❌ JSON 解析失败：", e)
        return None

if __name__ == '__main__':
    info= query_drug("6921793020362")
    print(info['data']['info']['name'])
