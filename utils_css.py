def inject_custom_css(st):
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #C7D3D4 !important;
            color: #02343F;
        }
        input, select, textarea {
            background-color: #F2EDD7 !important;
            border: 1px solid #02343F !important;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        input:focus, select:focus, textarea:focus {
            border-color: #FCF6F5 !important;
        }
        .stButton > button:active {
            transform: scale(0.98);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
