import streamlit as st

st.title("测试页面")
st.write("如果能看到这个，说明 Streamlit 工作正常")

# 测试导入
try:
    import ollama
    st.success("✅ ollama 导入成功")
    models = ollama.list()
    st.write(f"可用模型: {[m['model'] for m in models['models']]}")
except Exception as e:
    st.error(f"ollama 问题: {e}")