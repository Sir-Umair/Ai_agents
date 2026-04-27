import os

def read_log(path):
    if not os.path.exists(path):
        print(f"File {path} not found.")
        return
    
    encodings = ['utf-8', 'utf-16', 'utf-16-le', 'cp1252']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                content = f.read()
                print(f"--- Content of {path} (Encoding: {enc}) ---")
                print(content[-2000:]) # Last 2000 chars
                return
        except Exception:
            continue
    print(f"Could not read {path} with common encodings.")

if __name__ == "__main__":
    read_log("server_log.txt")
    read_log("server_log_new.txt")
    read_log("server_log_test.txt")
