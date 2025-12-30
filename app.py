import streamlit as st

# 페이지 설정
st.set_page_config(page_title="사출 게이트 계산기", layout="wide")

st.title("🚀 사출 게이트 제어 시간 계산기")
st.markdown("---")

# 1. 상단 기본 설정 (3열 배치)
st.subheader("1. 사출 기본 조건")
col1, col2, col3 = st.columns(3)

with col1:
    start_pos = st.number_input("계량 완료 위치 (mm)", value=150.0)
with col2:
    vp_pos = st.number_input("V-P 절환 위치 (mm)", value=20.0)
with col3:
    inj_time = st.number_input("실제 사출 시간 (sec)", value=3.5)

st.markdown("---")

# 2. 메인 화면 분할 (좌측: 입력, 우측: 결과)
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("2. 게이트 위치 입력 (60개)")
    gate_data = []
    
    # 2열로 나눠서 입력창 배치
    in_col1, in_col2 = st.columns(2)
    for i in range(1, 61):
        target_col = in_col1 if i <= 30 else in_col2
        with target_col:
            # 한 줄에 Open/Close를 넣기 위해 다시 컬럼 분할
            g_col1, g_col2, g_col3 = st.columns([1, 2, 2])
            g_col1.markdown(f"**G{i:02d}**")
            op = g_col2.text_input(f"Open", key=f"op_{i}", label_visibility="collapsed", placeholder="Open")
            cl = g_col3.text_input(f"Close", key=f"cl_{i}", label_visibility="collapsed", placeholder="Close")
            gate_data.append((op, cl))

with right_col:
    st.subheader("3. 계산 결과")
    dist = start_pos - vp_pos
    
    if dist <= 0:
        st.error("계량 위치가 V-P 위치보다 커야 합니다.")
    else:
        results = []
        for i, (op_val, cl_val) in enumerate(gate_data):
            if op_val and cl_val:
                try:
                    t_open = (start_pos - float(op_val)) / dist * inj_time
                    t_close = (start_pos - float(cl_val)) / dist * inj_time
                    results.append({
                        "Gate": f"Gate {i+1:02d}",
                        "Open Time(s)": round(t_open, 3),
                        "Close Time(s)": round(t_close, 3)
                    })
                except ValueError:
                    continue
        
        if results:
            st.table(results) # 표 형태로 깔끔하게 출력
        else:
            st.info("왼쪽에 위치값을 입력하면 결과가 여기에 표시됩니다.")

# 하단 리셋 버튼
if st.button("모든 데이터 초기화"):
    st.rerun()
