import tkinter as tk
from tkinter import messagebox, ttk

class InjectionValidatorDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("사출 게이트 계산기 - 입력 오류 감지 시스템")
        self.root.geometry("1150x850")
        self.root.configure(bg="#f8f9fa")

        # --- 1. 상단 기본 설정 ---
        top_frame = tk.LabelFrame(root, text=" 1. 사출 공정 기본 설정 ", padx=20, pady=15, font=("Malgun Gothic", 11, "bold"))
        top_frame.pack(fill="x", padx=20, pady=10)

        self.start_pos = tk.StringVar(value="150")
        self.vp_pos = tk.StringVar(value="20")
        self.inj_time = tk.StringVar(value="3.5")

        tk.Label(top_frame, text="계량 완료(mm):").grid(row=0, column=0, padx=5)
        tk.Entry(top_frame, textvariable=self.start_pos, width=10, justify='center').grid(row=0, column=1, padx=10)
        tk.Label(top_frame, text="V-P 위치(mm):").grid(row=0, column=2, padx=5)
        tk.Entry(top_frame, textvariable=self.vp_pos, width=10, justify='center').grid(row=0, column=3, padx=10)
        tk.Label(top_frame, text="사출 시간(sec):").grid(row=0, column=4, padx=5)
        tk.Entry(top_frame, textvariable=self.inj_time, width=10, justify='center').grid(row=0, column=5, padx=10)

        # --- 2. 메인 2분할 영역 ---
        main_container = tk.Frame(root, bg="#f8f9fa")
        main_container.pack(fill="both", expand=True, padx=20)

        # [좌측] 입력창
        left_frame = tk.LabelFrame(main_container, text=" 2. 입력 (Open > Close 필수) ", padx=10, pady=10, fg="blue", font=("Malgun Gothic", 11, "bold"))
        left_frame.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(left_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas)
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.gate_inputs = []
        for i in range(60):
            col_offset = (i // 30) * 3
            row = i % 30
            
            f = tk.Frame(self.scroll_frame, pady=1)
            f.grid(row=row, column=col_offset, padx=5)
            
            tk.Label(f, text=f"G{i+1:02d}", width=4).pack(side="left")
            op_ent = tk.Entry(f, width=8, justify='center')
            op_ent.pack(side="left", padx=2)
            cl_ent = tk.Entry(f, width=8, justify='center')
            cl_ent.pack(side="left", padx=2)
            
            # 실시간 검증을 위해 엔트리 저장
            self.gate_inputs.append({'op': op_ent, 'cl': cl_ent, 'label': f"Gate {i+1}"})

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # [우측] 결과창
        right_frame = tk.LabelFrame(main_container, text=" 3. 계산 결과 ", padx=10, pady=10, fg="green", font=("Malgun Gothic", 11, "bold"))
        right_frame.pack(side="right", fill="both", padx=(10, 0))

        cols = ("Gate", "Open(s)", "Close(s)", "Status")
        self.result_tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=25)
        for col in cols:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=90, anchor="center")
        
        self.result_tree.pack(side="left", fill="both", expand=True)

        # --- 3. 하단 버튼 ---
        btn_frame = tk.Frame(root, pady=15)
        btn_frame.pack(fill="x", padx=20)

        tk.Button(btn_frame, text="모두 지우기", command=self.clear_all).pack(side="left")
        tk.Button(btn_frame, text="데이터 검증 및 계산 실행", command=self.calculate, 
                  bg="#007bff", fg="white", font=("Malgun Gothic", 12, "bold"), height=2).pack(side="right", fill="x", expand=True, padx=(20, 0))

    def calculate(self):
        try:
            s = float(self.start_pos.get())
            v = float(self.vp_pos.get())
            t = float(self.inj_time.get())
            dist = s - v

            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            error_count = 0
            for i, gate in enumerate(self.gate_inputs):
                op_raw = gate['op'].get().strip()
                cl_raw = gate['cl'].get().strip()

                # 기본 배경색으로 초기화
                gate['op'].config(bg="white")
                gate['cl'].config(bg="white")

                if op_raw and cl_raw:
                    op_val = float(op_raw)
                    cl_val = float(cl_raw)

                    # 조건 검사: 오픈 위치 > 클로즈 위치여야 함 (사출은 전진하므로 숫자가 작아짐)
                    if op_val <= cl_val:
                        gate['op'].config(bg="#ffcccc") # 연빨강 배경
                        gate['cl'].config(bg="#ffcccc")
                        self.result_tree.insert("", "end", values=(f"G{i+1:02d}", "-", "-", "ERROR"), tags=('error',))
                        error_count += 1
                    else:
                        t_open = (s - op_val) / dist * t
                        t_close = (s - cl_val) / dist * t
                        self.result_tree.insert("", "end", values=(f"G{i+1:02d}", f"{t_open:.3f}", f"{t_close:.3f}", "OK"))

            self.result_tree.tag_configure('error', foreground='red')
            
            if error_count > 0:
                messagebox.showwarning("입력 오류", f"{error_count}개의 게이트 설정이 잘못되었습니다.\n오픈 위치는 클로즈 위치보다 커야 합니다.")

        except ValueError:
            messagebox.showerror("오류", "숫자 형식을 확인해 주세요.")

    def clear_all(self):
        for gate in self.gate_inputs:
            gate['op'].delete(0, tk.END)
            gate['cl'].delete(0, tk.END)
            gate['op'].config(bg="white")
            gate['cl'].config(bg="white")
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = InjectionValidatorDemo(root)
    root.mainloop()
