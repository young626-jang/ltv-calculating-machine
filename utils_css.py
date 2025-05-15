def inject_custom_css():
    st.markdown("""
        <style>
        /* ✅ 전체 배경색 */
        html, body, .stApp {
            background-color: #C7D3D4 !important;
            color: #02343F !important;
        }

        /* ✅ 입력창, 셀렉트 박스 스타일 */
        input, select, textarea {
            background-color: #F2EDD7 !important;
            border: 1px solid #02343F !important;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        }

        /* ✅ 입력창 포커스 스타일 */
        input:focus, select:focus, textarea:focus {
            border-color: #FCF6F5 !important;
            outline: none !important;
        }

        /* ✅ 버튼 스타일 */
        .stButton > button {
            background-color: #02343F !important;
            color: #F2EDD7 !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            border: none !important;
            font-weight: bold;
        }

        .stButton > button:hover {
            background-color: #011f2a !important;
        }

        .stButton > button:active {
            transform: scale(0.97);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        /* ✅ Expander header 스타일 */
        .streamlit-expanderHeader {
            font-weight: bold;
            color: #02343F;
            background-color: #F2EDD7 !important;
            border-radius: 5px;
        }

        /* ✅ 텍스트 에어리어 자동 크기 조절 */
        textarea {
            min-height: 150px !important;
        }
        </style>
    """, unsafe_allow_html=True)
