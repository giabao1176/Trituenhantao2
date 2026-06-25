import os
import sys
import io

# Force UTF-8 encoding for stdout/stderr to support Vietnamese printing on Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

os.environ['HF_HOME'] = "D:/HuggingFace_Models"

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- CHỈ NẠP MÔ HÌNH DỊCH (ENVIT5) ---
print("Đang nạp mô hình Dịch Envit5...")
envit5_name = "VietAI/envit5-translation"
tokenizer_vi = AutoTokenizer.from_pretrained(envit5_name)
model_vi = AutoModelForSeq2SeqLM.from_pretrained(envit5_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_vi.to(device)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "lich_su_dich.txt")

def is_duplicate(source_text):
    if not os.path.exists(HISTORY_FILE): return False
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return f"Nguồn: {source_text}" in f.read()
    except: return False

def save_to_notepad(source, translation):
    if is_duplicate(source.strip()):
        print(f"-> Đã có trong lịch sử, không lưu trùng: {source[:30]}...")
        return
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}]\nNguồn: {source}\nDịch: {translation}\n" + "-"*50 + "\n")
            print(f"-> Đã lưu vào Notepad: {HISTORY_FILE}")
    except Exception as e: print(f"Lỗi lưu file: {e}")

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        text = data.get('text', '').strip()
        direction = data.get('direction', 'en: ')
        
        # Luôn dùng tiền tố tiêu chuẩn để đảm bảo Envit5 dịch đúng tiếng Việt
        input_text = direction + text
        
        # Nếu là từ đơn, chúng ta có thể thử dùng một prompt "mẹo" hơn một chút
        is_single_word = len(text.split()) == 1
        
        inputs = tokenizer_vi(input_text, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = model_vi.generate(inputs.input_ids, max_length=512)
        
        result = tokenizer_vi.decode(outputs[0], skip_special_tokens=True)
        
        # Làm sạch kết quả
        if result.startswith("en: "): result = result[4:]
        if result.startswith("vi: "): result = result[4:]
        
        # Nếu là từ đơn và bản dịch chưa có loại từ, ta có thể bổ sung nếu thấy các từ khóa quen thuộc
        if is_single_word:
            # Chuyển đổi một số nhãn tiếng Anh sang tiếng Việt nếu mô hình có trả về
            result = result.replace("Noun", "(Danh từ)") \
                           .replace("Verb", "(Động từ)") \
                           .replace("Adjective", "(Tính từ)") \
                           .replace("Adverb", "(Trạng từ)")
        
        save_to_notepad(text, result)
        return jsonify({"translation": result})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/explain', methods=['POST'])
def explain():
    try:
        data = request.json
        word = data.get('word', '')
        prompt = f"vi: giải thích nghĩa của từ '{word}' và cho ví dụ"
        inputs = tokenizer_vi(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model_vi.generate(inputs.input_ids, max_length=512)
        explanation = tokenizer_vi.decode(outputs[0], skip_special_tokens=True)
        return jsonify({"explanation": explanation})
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Server dịch thuật sẵn sàng tại http://localhost:5000")
    app.run(port=5000)
