"""
CIFE Edu-Suite - Debug Test
============================
Run this to diagnose HTML rendering issues in Streamlit.

Usage: streamlit run debug_test.py
"""

import streamlit as st

st.set_page_config(page_title="Debug Test", layout="wide")

st.title("🔧 Streamlit HTML Rendering Debug Test")

# Test 1: Basic HTML
st.header("Test 1: Basic HTML Rendering")
basic_html = '<div style="background:blue;color:white;padding:10px;border-radius:8px;">If you see this as a blue box, basic HTML works!</div>'
st.markdown(basic_html, unsafe_allow_html=True)

# Test 2: Multi-line HTML (the problematic pattern)
st.header("Test 2: Multi-line HTML (like wizard steps)")
multiline_html = """
<div style="
    background: green;
    color: white;
    padding: 10px;
    border-radius: 8px;
">
    If this is a green box, multi-line HTML works!
</div>
"""
st.markdown(multiline_html, unsafe_allow_html=True)

# Test 3: Single-line condensed HTML
st.header("Test 3: Single-line Condensed HTML")
singleline_html = '<div style="background:purple;color:white;padding:10px;border-radius:8px;">If this is a purple box, single-line HTML works!</div>'
st.markdown(singleline_html, unsafe_allow_html=True)

# Test 4: Nested HTML with flexbox
st.header("Test 4: Nested Flexbox HTML")
flexbox_html = '<div style="display:flex;gap:10px;"><div style="background:#4F46E5;color:white;padding:20px;border-radius:50%;width:50px;height:50px;display:flex;align-items:center;justify-content:center;">1</div><div style="background:#E5E7EB;color:#6B7280;padding:20px;border-radius:50%;width:50px;height:50px;display:flex;align-items:center;justify-content:center;">2</div></div>'
st.markdown(flexbox_html, unsafe_allow_html=True)

# Test 5: The exact wizard pattern (condensed)
st.header("Test 5: Wizard Steps Pattern (Fixed)")
wizard_html = '<div style="display:flex;justify-content:center;align-items:flex-start;gap:0;margin:2rem 0;"><div style="display:flex;flex-direction:column;align-items:center;gap:0.5rem;"><div style="width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.2rem;font-weight:700;background:#4F46E5;color:white;">1</div><div style="font-size:0.9rem;text-align:center;color:#4F46E5;font-weight:600;">Step 1</div></div><div style="width:60px;height:3px;background:#E5E7EB;margin-top:23px;"></div><div style="display:flex;flex-direction:column;align-items:center;gap:0.5rem;"><div style="width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.2rem;font-weight:700;background:#E5E7EB;color:#6B7280;">2</div><div style="font-size:0.9rem;text-align:center;color:#9CA3AF;font-weight:500;">Step 2</div></div></div>'
st.markdown(wizard_html, unsafe_allow_html=True)

# Summary
st.divider()
st.header("📋 Diagnosis Summary")
st.markdown("""
**What to check:**

1. ✅ If Test 1 shows a **blue box** → Basic HTML works
2. ⚠️ If Test 2 shows **raw HTML code** → Multi-line HTML is broken (this is likely your issue!)
3. ✅ If Test 3 shows a **purple box** → Single-line HTML works
4. ✅ If Test 4 shows **two circles** → Flexbox works
5. ✅ If Test 5 shows **wizard steps** → The fix should work

**If Test 2 fails but others work:**
The issue is that multi-line HTML strings with newlines and indentation are being escaped.
The fix is to condense all HTML to single lines or use `.join()` for building HTML.

**Streamlit Version:**
""")

st.code(f"Streamlit version: {st.__version__}")

st.markdown("""
**If all tests fail:**
- Check that `unsafe_allow_html=True` is being passed
- Check for browser extensions that might block inline styles
- Try a different browser or incognito mode
""")
