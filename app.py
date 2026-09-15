import streamlit as st

pg = st.navigation([
    st.Page("exercise.py", title="Day 2", icon="💬"),
    
    # เผื่อไว้ วันต่อไปแค่เพิ่มบรรทัดแบบนี้
    # st.Page("exercise_day1.py", title="Day 1", icon="📝"),
])
pg.run()