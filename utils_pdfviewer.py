import streamlit as st
from utils_pdf import pdf_to_image

def pdf_viewer_with_navigation(st, path, total_pages):
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 0

    def display_page(page_num, col):
        try:
            img = pdf_to_image(path, page_num)
            col.image(img, caption=f"Page {page_num + 1} of {total_pages}")
        except Exception as e:
            col.error(f"페이지를 로드할 수 없습니다: {e}")

    # Display current and next page
    col1, col2 = st.columns(2)
    if st.session_state["current_page"] < total_pages:
        display_page(st.session_state["current_page"], col1)

    if st.session_state["current_page"] + 1 < total_pages:
        display_page(st.session_state["current_page"] + 1, col2)

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀ 이전 페이지", disabled=(st.session_state["current_page"] == 0)):
            st.session_state["current_page"] -= 1

    with col2:
        if st.button("다음 페이지 ▶", disabled=(st.session_state["current_page"] >= total_pages - 1)):
            st.session_state["current_page"] += 1