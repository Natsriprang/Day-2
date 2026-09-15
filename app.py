import streamlit as st

pg = st.navigation([
    st.Page("exercise.py", title="Day 2", icon="💬"),
    st.Page("exercise2.1.py", title="Exercise 2.1"),
    st.Page("exercise2.2.py", title="Exercise 2.2"),
    st.Page("exercise2.3.py", title="Exercise 2.3")
    # เผื่อไว้ วันต่อไปแค่เพิ่มบรรทัดแบบนี้
    # st.Page("exercise_day1.py", title="Day 1", icon="📝"),
])
pg.run()