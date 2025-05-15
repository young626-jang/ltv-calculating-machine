import streamlit as st
from utils_pdf import pdf_to_image

def pdf_viewer_with_navigation(st, path, total_pages):
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 0

    col1, col2 = st.columns(2)
    if st.session_state["current_page"] < total_pages:
        img_left = pdf_to_image(path, st.session_state["current_page"])
        col1.image(img_left, caption=f"Page {st.session_state['current_page'] + 1} of {total_pages}")

    if st.session_state["current_page"] + 1 < total_pages:
        img_right = pdf_to_image(path, st.session_state["current_page"] + 1)
        col2.image(img_right, caption=f"Page {st.session_state['current_page'] + 2} of {total_pages}")

    # 버튼은 열 나눠서 좌/우 박음 (Viewer 내부)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("◀ 이전 페이지", key="prev_page", use_container_width=True):
            if st.session_state["current_page"] > 0:
                st.session_state["current_page"] -= 1
    with col2:
        if st.button("다음 페이지 ▶", key="next_page", use_container_width=True):
            if st.session_state["current_page"] < total_pages - 1:
                st.session_state["current_page"] += 1
