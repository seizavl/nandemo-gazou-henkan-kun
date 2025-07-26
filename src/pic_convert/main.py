import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np

# 対応形式一覧
formats = ['png', 'jpg', 'jpeg', 'bmp', 'tga', 'webp', 'gif',"ico"]

def convert_image(file_path, target_format):
    try:
        base, _ = os.path.splitext(file_path)
        output_file = f"{base}.{target_format}"
        with Image.open(file_path) as im:
            im.convert('RGB').save(output_file, target_format.upper() if target_format != 'jpg' else 'JPEG')
        os.remove(file_path)
        return output_file
    except Exception as e:
        return str(e)

def make_transparent(file_path, color_to_remove):
    try:
        base, _ = os.path.splitext(file_path)
        output_file = f"{base}_transparent.png"
        
        with Image.open(file_path) as img:
            img = img.convert("RGBA")
            data = np.array(img)
            
            red, green, blue = color_to_remove
            tolerance = 30
            
            mask = (np.abs(data[:, :, 0] - red) < tolerance) & \
                   (np.abs(data[:, :, 1] - green) < tolerance) & \
                   (np.abs(data[:, :, 2] - blue) < tolerance)
            
            data[mask] = [0, 0, 0, 0]
            
            transparent_img = Image.fromarray(data, 'RGBA')
            transparent_img.save(output_file, 'PNG')
            
        return output_file
    except Exception as e:
        return str(e)

def show_image_preview(file_path, root):
    """画像プレビューでスポイト機能を提供"""
    preview_window = tk.Toplevel(root)
    preview_window.title("なんでも画像変換くん")
    preview_window.configure(bg='#1a1a1a')
    preview_window.overrideredirect(True)
    window_width = 900
    window_height = 700
    x = (1920 // 2) - (window_width // 2)
    y = (1080 // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    # プレビューウィンドウ用のクローズボタン
    close_frame = tk.Frame(preview_window, bg='#1a1a1a', height=40)
    close_frame.pack(fill='x')
    close_frame.pack_propagate(False)
    
    close_btn = tk.Button(close_frame, text="✕", 
                         font=('Meiryo', 16, 'bold'),
                         bg='#ff4757', fg='white',
                         relief='flat', width=3, height=1,
                         cursor='hand2',
                         command=preview_window.destroy)
    close_btn.pack(side='right', padx=10, pady=5)
    
    # モダンなスタイル設定
    preview_window.resizable(True, True)
    
    # 画像を読み込み、表示用にリサイズ
    original_img = Image.open(file_path)
    display_img = original_img.copy()
    
    # 表示用サイズ計算
    max_width, max_height = 700, 500
    img_width, img_height = display_img.size
    
    if img_width > max_width or img_height > max_height:
        ratio = min(max_width/img_width, max_height/img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        display_img = display_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    scale_x = img_width / display_img.size[0]
    scale_y = img_height / display_img.size[1]
    
    photo = ImageTk.PhotoImage(display_img)
    
    # ヘッダーフレーム
    header_frame = tk.Frame(preview_window, bg='#1a1a1a', height=80)
    header_frame.pack(fill='x', padx=20, pady=(20, 0))
    header_frame.pack_propagate(False)
    
    # タイトル
    title_label = tk.Label(header_frame, text="🎨 Color Picker", 
                          font=('Meiryo', 24, 'bold'), 
                          fg='#ffffff', bg='#1a1a1a')
    title_label.pack(side='left', pady=10)
    
    # 説明
    info_label = tk.Label(header_frame, text="消したい色を選んでください", 
                         font=('Meiryo', 12), 
                         fg='#888888', bg='#1a1a1a')
    info_label.pack(side='left', padx=(20, 0), pady=10)
    
    # カラー情報表示エリア
    color_frame = tk.Frame(preview_window, bg='#2d2d2d', height=60)
    color_frame.pack(fill='x', padx=20, pady=10)
    color_frame.pack_propagate(False)
    
    color_display = tk.Frame(color_frame, bg='#ffffff', width=40, height=40)
    color_display.pack(side='left', padx=15, pady=10)
    color_display.pack_propagate(False)
    
    color_info = tk.Label(color_frame, text="画像の上にカーソルを移動してください", 
                        font=('Meiryo', 14), fg='#ffffff', bg='#2d2d2d')

    color_info.pack(side='left', padx=(15, 0), pady=10)
    
    # 画像表示エリア
    canvas_frame = tk.Frame(preview_window, bg='#1a1a1a')
    canvas_frame.pack(expand=True, fill='both', padx=20, pady=10)
    
    canvas = tk.Canvas(canvas_frame, 
                      width=display_img.size[0], 
                      height=display_img.size[1],
                      bg='#1a1a1a',
                      highlightthickness=0,
                      relief='flat')
    canvas.pack(expand=True)
    canvas.create_image(display_img.size[0]//2, display_img.size[1]//2, image=photo)
    
    def on_click(event):
        x, y = event.x - (canvas.winfo_width() - display_img.size[0]) // 2, event.y - (canvas.winfo_height() - display_img.size[1]) // 2
        
        orig_x = int(x * scale_x)
        orig_y = int(y * scale_y)
        
        if 0 <= orig_x < img_width and 0 <= orig_y < img_height:
            pixel_color = original_img.getpixel((orig_x, orig_y))
            if len(pixel_color) == 3:
                r, g, b = pixel_color
            else:
                r, g, b = pixel_color[:3]
            
            # モダンな確認ダイアログ
            result = messagebox.askyesno("透明化の確認", 
                             f"RGB({r}, {g}, {b}) を透明にしますか？\n\n透明部分を含む新しい PNG ファイルが作成されます。",
                             icon='question')

            if result:
                processed_result = make_transparent(file_path, (r, g, b))
                if os.path.exists(processed_result):
                    messagebox.showinfo("完了", f"成功しました")
                    preview_window.destroy()
                    root.destroy()
                else:
                    messagebox.showerror("✗ Error", f"失敗しました")
    
    def on_motion(event):
        x, y = event.x - (canvas.winfo_width() - display_img.size[0]) // 2, event.y - (canvas.winfo_height() - display_img.size[1]) // 2
        orig_x = int(x * scale_x)
        orig_y = int(y * scale_y)
        
        if 0 <= orig_x < img_width and 0 <= orig_y < img_height:
            pixel_color = original_img.getpixel((orig_x, orig_y))
            if len(pixel_color) == 3:
                r, g, b = pixel_color
            else:
                r, g, b = pixel_color[:3]
            
            # カラー表示を更新
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            color_display.configure(bg=hex_color)
            color_info.configure(text=f"RGB({r}, {g}, {b})  •  {hex_color.upper()}")
        else:
            color_info.configure(text="画像の上にカーソルを移動してください")
            color_display.configure(bg='#ffffff')
    
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<Motion>", on_motion)
    
    # ボタンエリア
    button_frame = tk.Frame(preview_window, bg='#1a1a1a', height=80)
    button_frame.pack(fill='x', padx=20, pady=(0, 20))
    button_frame.pack_propagate(False)
    
    cancel_btn = tk.Button(button_frame, text="✕ Cancel", 
                          font=('Meiryo', 12, 'bold'),
                          bg='#ff4757', fg='white',
                          relief='flat', padx=30, pady=12,
                          cursor='hand2',
                          command=preview_window.destroy)
    cancel_btn.pack(side='right', pady=20)
    
    preview_window.photo = photo

def show_gui(file_path):
    root = tk.Tk()
    root.configure(bg='#0f0f23')
    root.resizable(False, False)
    root.overrideredirect(True)
    
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 600
    window_height = 700
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 右上にクローズボタンを配置するためのフレーム
    close_frame = tk.Frame(root, bg='#0f0f23', height=40)
    close_frame.pack(fill='x')
    close_frame.pack_propagate(False)
    
    # 右上のクローズボタン
    close_btn = tk.Button(close_frame, text="✕", 
                         font=('Meiryo', 16, 'bold'),
                         bg='#0f0f23', fg='white',
                         relief='flat', width=3, height=1,
                         cursor='hand2',
                         command=root.destroy)
    close_btn.pack(side='right', padx=10, pady=5)
    
    # メインコンテナ
    main_container = tk.Frame(root, bg='#0f0f23')
    main_container.pack(expand=True, fill='both', padx=30, pady=(0, 30))
    
    # ヘッダー
    header_frame = tk.Frame(main_container, bg='#0f0f23')
    header_frame.pack(fill='x', pady=(0, 30))
    
    title = tk.Label(header_frame, text="🎨 なんでも画像変換くん", 
                    font=('Meiryo', 28, 'bold'), 
                    fg='#ffffff', bg='#0f0f23')
    title.pack()

    
    # ファイル情報
    file_info_frame = tk.Frame(main_container, bg='#1a1a2e', relief='flat')
    file_info_frame.pack(fill='x', pady=(0, 30))
    
    file_label = tk.Label(file_info_frame, text=f"📁 {os.path.basename(file_path)}", 
                         font=('Meiryo', 14, 'bold'), 
                         fg='#4eeaa7', bg='#1a1a2e')
    file_label.pack(pady=15)
    
    # 形式変換セクション
    format_section = tk.Frame(main_container, bg='#0f0f23')
    format_section.pack(fill='x', pady=(0, 30))
    
    format_title = tk.Label(format_section, text="⚡ 変換形式", 
                           font=('Meiryo', 18, 'bold'), 
                           fg='#ffffff', bg='#0f0f23')
    format_title.pack(anchor='w', pady=(0, 15))
    
    # フォーマットボタンのグリッド
    format_grid = tk.Frame(format_section, bg='#0f0f23')
    format_grid.pack(fill='x')
    
    def select(fmt):
        result = convert_image(file_path, fmt)
        if os.path.exists(result):
            messagebox.showinfo("✓ Conversion Complete", f"Successfully converted to {fmt.upper()}!\n\nSaved as: {os.path.basename(result)}")
        else:
            messagebox.showerror("✗ Conversion Failed", f"Failed to convert image:\n{result}")
        root.destroy()
    
    # モダンなボタンスタイル
    button_colors = {
        'png': '#3742fa', 'jpg': '#ff6348', 'jpeg': '#ff6348', 
        'bmp': '#ffa502', 'tga': '#2ed573', 'webp': '#5f27cd', 'gif': '#ff3838'
    }
    
    for i, fmt in enumerate(formats):
        row = i // 4
        col = i % 4
        
        btn = tk.Button(format_grid, text=fmt.upper(), 
                       font=('Meiryo', 11, 'bold'),
                       bg=button_colors.get(fmt, '#6c7293'), 
                       fg='white',
                       relief='flat', 
                       width=8, height=2,
                       cursor='hand2',
                       activebackground='#ffffff',
                       activeforeground='#000000',
                       command=lambda f=fmt: select(f))
        btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
    
    # グリッドの列を均等に配置
    for i in range(4):
        format_grid.columnconfigure(i, weight=1)
    
    # 透過処理セクション
    transparency_section = tk.Frame(main_container, bg='#0f0f23')
    transparency_section.pack(fill='x', pady=(30, 0))
    
    transparency_title = tk.Label(transparency_section, text="✨ 画像処理", 
                                 font=('Meiryo', 18, 'bold'), 
                                 fg='#ffffff', bg='#0f0f23')
    transparency_title.pack(anchor='w', pady=(0, 15))
    
    # スポイトボタン
    def open_preview():
        show_image_preview(file_path, root)
    
    eyedropper_btn = tk.Button(transparency_section, text="🎨 透過処理", 
                              font=('Meiryo', 14, 'bold'),
                              bg='#4eeaa7', fg='#0f0f23',
                              relief='flat', 
                              height=3,
                              cursor='hand2',
                              activebackground='#2ed573',
                              activeforeground='#ffffff',
                              command=open_preview)
    eyedropper_btn.pack(fill='x', pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        show_gui(sys.argv[1])
    else:
        messagebox.showerror("Error")