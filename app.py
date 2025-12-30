import streamlit as st
import pandas as pd

# 페이지 설정 (전체 화면 사용 및 타이틀)
st.set_page_config(page_title="사출 게이트 계산기", layout="wide")

st.title("⚙️ 사출 게이트 제어 시간 계산기 (60 Gates)")
st.info("오픈 위치는 클로즈 위치보다 커야 합니다. 오류 시 입력창이 붉게 표시됩니다.")

# --- 1. 상단 기본 설정 영역 ---
with st.container():
    st.subheader("📍 1. 사출 기본 조건")
    c1, c2, c3 = st.columns(3)
    with c1:
        start_pos = st.number_input("계량 완료 위치 (mm)", value=150.0, step=0.1)
    with c2:
        vp_pos = st.number_input("V-P 절환 위치 (mm)", value=20.0, step=0.1)
    with c3:
        inj_time = st.number_input("실제 사출 시간 (sec)", value=3.5, step=0.01)

st.divider()

# --- 2. 메인 화면 분할 (좌측: 입력 / 우측: 결과) ---
left_col, right_col = st.columns([0.6, 0.4])

with left_col:
    st.subheader("📥 2. 게이트 위치 입력")
    # 3열로 배치하여 60개를 콤팩트하게 보여줌
    in_col1, in_col2, in_col3 = st.columns(3)
    
    gate_data = []
    total_gates = 60
    
    for i in range(1, total_gates + 1):
        # 20개씩 열 나누기
        if i <= 20: target_col = in_col1
        elif i <= 40: target_col = in_col2
        else: target_col = in_col3
        
        with target_col:
            g_c1, g_c2, g_c3 = st.columns([1, 2, 2])
            g_c1.markdown(f"<br>**G{i:02d}**", unsafe_allow_html=True)
            
            # 입력값 받기
            op = st.text_input(f"G{i} Open", key=f"op_{i}", label_visibility="collapsed", placeholder="Open")
            cl = st.text_input(f"G{i} Close", key=f"cl_{i}", label_visibility="collapsed", placeholder="Close")
            
            # 오류 검증 로직
            error = False
            if op and cl:
                try:
                    if float(op) <= float(cl):
                        error = True
                        # CSS를 이용해 입력창 테두리를 빨간색으로 변경
                        st.markdown(f"""
                            <style>
                            div[data-testid="stTextInput"] > div:nth-of-type(1) input[aria-label="G{i} Open"],
                            div[data-testid="stTextInput"] > div:nth-of-type(1) input[aria-label="G{i} Close"] {{
                                border: 2px solid red !important;
                                background-color: #ffe6e6 !important;
                            }}
                            </style>
                        """, unsafe_allow_html=True)
                except ValueError:
                    pass
            
            gate_data.append({"id": i, "op": op, "cl": cl, "error": error})

with right_col:
    st.subheader("📤 3. 계산 결과")
    dist = start_pos - vp_pos
    
    if dist <= 0:
        st.error("오류: 계량 완료 위치가 V-P 위치보다 커야 합니다.")
    else:
        results = []
        for g in gate_data:
            if g["op"] and g["cl"]:
                if g["error"]:
                    results.append({"Gate": f"G{g['id']:02d}", "Open(s)": "⚠️ERROR", "Close(s)": "⚠️ERROR", "Status": "Check Order"})
                else:
                    try:
                        t_open = (start_pos - float(g["op"])) / dist * inj_time
                        t_close = (start_pos - float(g["cl"])) / dist * inj_time
                        results.append({
                            "Gate": f"G{g['id']:02d}", 
                            "Open(s)": round(t_open, 3), 
                            "Close(s)": round(t_close, 3),
                            "Status": "✅ OK"
                        })
                    except ValueError:
                        continue
        
        if results:
            df = pd.DataFrame(results)
            # 상태에 따라 색상을 입힌 테이블 출력
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # 엑셀 다운로드 버튼 추가
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("💾 결과 다운로드 (CSV)", csv, "injection_results.csv", "
