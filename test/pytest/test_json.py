import json
import subprocess
import os
import pytest


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    END = '\033[0m'

def banner(text):
    print(f"\n{Colors.PURPLE}{'='*50}")
    print(f"  🚀 {text}")
    print(f"{'='*50}{Colors.RESET}\n")

def section(text):
    print(f"{Colors.BLUE}🔍 {text}{Colors.RESET}")
    print(f"{'-'*30}")

def extract_messages_with_json_lines(parsed_data):
    all_messages = {"Error": {}, "Warning": {}, "Info": {}}
    
    with open("parsed_logs.json", 'r') as f:
        json_lines = f.readlines()
    
    for filename, file_data in parsed_data.items():
        for category in ["Error", "Warning", "Info"]:
            if category in file_data:
                for line_num, message in file_data[category].items():
                    json_line_num = None
                    for i, json_line in enumerate(json_lines, 1):
                        if f'"{line_num}": "{message}"' in json_line:
                            json_line_num = i
                            break
                    
                    all_messages[category][message] = {
                        "line": line_num, 
                        "file": filename,
                        "json_line": json_line_num
                    }
    return all_messages

def run_tcl():
    try:
        subprocess.run(["tclsh", "bin/parse_logs.tcl", "-path", "example"], 
                      capture_output=True, check=True)
        return True
    except:
        return False

def test_all_messages_exist_in_golden():
    banner("TCL LOG PARSER TEST")
    
    section("Running TCL Script")
    if run_tcl():
        print(f"{Colors.GREEN}✅ TCL script OK{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ TCL script failed{Colors.RESET}")
        pytest.fail("TCL script failed to run")
    
    section("Loading Files")
    try:
        with open("parsed_logs.json", 'r') as f:
            parsed_data = json.load(f)
        print(f"{Colors.GREEN}✅ Loaded parsed_logs.json{Colors.RESET}")
        
        with open("test/golden/golden.json", 'r') as f:
            golden_data = json.load(f)
        print(f"{Colors.GREEN}✅ Loaded golden.json{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error loading files: {e}{Colors.RESET}")
        pytest.fail(f"Error loading files: {e}")
    
    section("Checking Messages")
    parsed_messages = extract_messages_with_json_lines(parsed_data)
    found = {"Error": 0, "Warning": 0, "Info": 0}
    category_icons = {"Error": "🔴", "Warning": "🟡", "Info": "🔵"}
    missing_messages = []
    
    for category in ["Error", "Warning", "Info"]:
        golden_msgs = golden_data.get(category, {})
        parsed_msgs = parsed_messages.get(category, {})
        
        print(f"\n{category_icons[category]} {Colors.BOLD}{category}:{Colors.RESET}")
        
        if not parsed_msgs:
            print(f"  {Colors.CYAN}ℹ️  No {category.lower()} messages found{Colors.RESET}")
            continue
            
        for message, info in parsed_msgs.items():
            log_line_num = info["line"]
            filename = info["file"]
            json_line_num = info["json_line"]
            
            if message in golden_msgs.values():
                print(f"  {Colors.GREEN}✅ {message}{Colors.RESET}")
                print(f"    {Colors.CYAN}📄 Log: {filename} line {log_line_num}{Colors.RESET}")
                print(f"    {Colors.BLUE}📋 JSON: parsed_logs.json line {json_line_num}{Colors.RESET}")
                found[category] += 1
            else:
                print(f"  {Colors.RED}❌ {message} (NOT FOUND IN GOLDEN){Colors.RESET}")
                print(f"    {Colors.YELLOW}📄 Log: {filename} line {log_line_num}{Colors.RESET}")
                print(f"    {Colors.RED}📋 JSON: parsed_logs.json line {json_line_num}{Colors.RESET}")
                missing_messages.append(f"{category}: '{message}' from {filename}:line{log_line_num} (JSON line {json_line_num})")
    
    section("Results")
    total_parsed = sum(len(parsed_messages[cat]) for cat in ["Error", "Warning", "Info"])
    total_found = sum(found.values())
    
    print(f"📊 Parsed: {Colors.CYAN}{total_parsed}{Colors.RESET}")
    print(f"✅ Found:  {Colors.GREEN}{total_found}{Colors.RESET}")
    print(f"❌ Missing: {Colors.RED}{total_parsed - total_found}{Colors.RESET}")
    

    if total_parsed == 0:
        print(f"{Colors.YELLOW}⚠️ No messages parsed from logs.{Colors.RESET}")
        pytest.fail("No messages parsed from logs")
        
    if missing_messages:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Missing Messages:{Colors.RESET}")
        for msg in missing_messages:
            print(f"  {Colors.RED}• {msg}{Colors.RESET}")
    
    if total_found == total_parsed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 SUCCESS! All messages match! 🎉{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}💥 FAIL! {total_parsed - total_found} missing! 💥{Colors.RESET}")
        assert False, f"{total_parsed - total_found} messages not found in golden file"

if __name__ == "__main__":
    test_all_messages_exist_in_golden()