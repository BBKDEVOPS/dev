import tkinter as tk
from tkinter import filedialog, messagebox, font
from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_cpp import Llama
import torch
import subprocess
import os

def load_models():
    """โหลดโมเดล Ollama"""
    model_paths = {
        "codellama-7b": "/path/to/codellama-7b.Q4_K_M.gguf",  # ปรับ path ตามตำแหน่งไฟล์โมเดลของคุณ
        # เพิ่มเติมโมเดลอื่นๆ ได้ตามต้องการ (ถ้ามี)
    }

    models = {}
    for model_name, model_path in model_paths.items():
        try:
            model = Llama(model_path=model_path, n_ctx=2048)  # ปรับ n_ctx ตามต้องการ
            models[model_name] = model
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model '{model_name}': {e}")
    return models, {}  # ส่งคืน tokenizers เป็น dict ว่างเปล่า เพราะ Ollama ไม่ใช้ tokenizer

# ฟังก์ชันสำหรับสร้างโค้ด (ปรับปรุง)
def generate_code(prompt, model_name="codellama-7b", max_length=1024):
    """สร้างโค้ดจาก prompt ที่กำหนด โดยใช้โมเดล Ollama"""
    try:
        if model_name not in models:
            raise ValueError(f"Invalid model name: {model_name}")

        model = models[model_name]

        # สร้างโค้ดโดยใช้ Ollama
        output = model(prompt, max_tokens=max_length, stop=["\n\n"])
        generated_code = output['text']
        return generated_code
    except (RuntimeError, ValueError) as e:
        if "CUDA out of memory" in str(e):
            messagebox.showerror("Error", "CUDA out of memory. Please try a smaller model or reduce the max_length.")
        else:
            messagebox.showerror("Error", f"An error occurred while generating code: {e}")
        return ""

# ฟังก์ชันสำหรับรันโค้ด
def run_code():
    """รันโค้ดที่อยู่ใน Text widget และแสดงผลลัพธ์"""
    code = code_text.get(1.0, tk.END).strip()
    if not code:
        messagebox.showwarning("Warning", "No code to run.")
        return

    try:
        result = subprocess.run(["python", "-c", code], capture_output=True, text=True)
        output_text.delete(1.0, tk.END)
        if result.returncode == 0:
            output_text.insert(tk.END, result.stdout)
        else:
            output_text.insert(tk.END, result.stderr)
    except FileNotFoundError:
        messagebox.showerror("Error", "Python interpreter not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while running code: {e}")

# ฟังก์ชันสำหรับเปิดไฟล์
def open_file():
    """เปิดไฟล์ Python และแสดงโค้ดใน Text widget"""
    filepath = filedialog.askopenfilename(
        filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
    )
    if not filepath:
        return

    try:
        with open(filepath, "r") as input_file:
            code = input_file.read()
            code_text.delete(1.0, tk.END)
            code_text.insert(tk.END, code)
    except FileNotFoundError:
        messagebox.showerror("Error", f"File not found: {filepath}")
    except PermissionError:
        messagebox.showerror("Error", f"Permission denied: {filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while opening the file: {e}")

# ฟังก์ชันสำหรับบันทึกไฟล์
def save_file():
    """บันทึกโค้ดจาก Text widget ลงไฟล์"""
    filepath = filedialog.asksaveasfilename(
        defaultextension="py", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
    )
    if not filepath:
        return

    try:
        with open(filepath, "w") as output_file:
            code = code_text.get(1.0, tk.END)
            output_file.write(code)
    except PermissionError:
        messagebox.showerror("Error", f"Permission denied: {filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

# ฟังก์ชันเมื่อกดปุ่ม "Generate Code" 
def generate_code_callback():
    """สร้างโค้ดเมื่อกดปุ่ม "สร้างโค้ด" """
    prompt = prompt_text.get(1.0, tk.END).strip()
    model_name = model_var.get()
    generated_code = generate_code(prompt, model_name)
    code_text.delete(1.0, tk.END)
    code_text.insert(tk.END, generated_code)

# ฟังก์ชันสำหรับเปลี่ยนภาษา
def change_language(language):
    """เปลี่ยนภาษาของ GUI"""
    global font_thai
    if language == "thai":
        font_thai = font.Font(family="TH SarabunPSK", size=12)
    elif language == "english":
        font_thai = font.Font(family="Courier New", size=12)
    else:
        font_thai = font.Font(family="Microsoft Sans Serif", size=12)

    for widget in frame.winfo_children():
        if isinstance(widget, tk.Text) or isinstance(widget, tk.Label):
            widget.config(font=font_thai)
    app.update()

# ฟังก์ชันหลักสำหรับสร้าง GUI และเริ่มต้นโปรแกรม
def main():
    global models, tokenizers, device, code_text, output_text, model_var, frame

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    models, tokenizers = load_models()

    # --- GUI ---

    app = tk.Tk()
    app.title("AI Code Generator")

    # ตรวจสอบฟอนต์ที่รองรับภาษาไทย
    if font.families().__contains__("TH SarabunPSK"):
        font_thai = font.Font(family="TH SarabunPSK", size=12)
    else:
        font_thai = font.Font(family="Microsoft Sans Serif", size=12)

    frame = tk.Frame(app)
    frame.pack(padx=10, pady=10)

    # ... (ส่วนของการสร้างวิดเจ็ตต่างๆ เหมือนเดิม) ...

    app.mainloop()

# เริ่มต้นโปรแกรม
if __name__ == "__main__":
    main()