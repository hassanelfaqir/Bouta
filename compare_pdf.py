import streamlit as st
import pdfplumber
import re
import pandas as pd

st.set_page_config(page_title="🧾 مقارنة الأكواد بين ملفين PDF", page_icon="📄")

st.markdown("<h1 style='text-align:center;'>🧾 مقارنة الأكواد بين ملفي الفواتير (FCT / FL)</h1>", unsafe_allow_html=True)

pdf1 = st.file_uploader("📁 الملف الأول (فاتورة FCT)", type="pdf")
pdf2 = st.file_uploader("📁 الملف الثاني (فاتورة FL)", type="pdf")

# ------------------------------------------------------
# دالة لاستخراج الأكواد من النص داخل PDF
# ------------------------------------------------------
def extract_codes(pdf_file):
    codes = set()
    if not pdf_file:
        return codes

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            # نلقط الأكواد اللي فيها OSC- أو ECHANGE-OSC-
            found = re.findall(r"(ECHANGE-?OSC-[0-9\-]+|OSC-[0-9\-]+)", text, flags=re.IGNORECASE)
            for f in found:
                codes.add(f.strip().upper())
    return codes


if pdf1 and pdf2:
    with st.spinner("⏳ جاري استخراج الأكواد من الملفات..."):
        codes_fct = extract_codes(pdf1)
        codes_fl = extract_codes(pdf2)

    if not codes_fct or not codes_fl:
        st.error("⚠️ ما قدرش يلقى الأكواد فواحد من الملفات. تأكد أن الملفات فيها الأكواد (مثلاً OSC-...).")
    else:
        # المقارنة
        missing_in_fct = sorted(codes_fl - codes_fct)
        missing_in_fl = sorted(codes_fct - codes_fl)

        st.success("✅ تمت المقارنة بنجاح!")

        if missing_in_fct:
            st.markdown("### ❌ الأكواد اللي ناقصة في ملف FCT:")
            st.dataframe(pd.DataFrame(missing_in_fct, columns=["Code ناقص في FCT"]))
        else:
            st.info("📗 جميع الأكواد من FL موجودة في FCT.")

        if missing_in_fl:
            st.markdown("### ❌ الأكواد اللي ناقصة في ملف FL:")
            st.dataframe(pd.DataFrame(missing_in_fl, columns=["Code ناقص في FL"]))
        else:
            st.info("📗 جميع الأكواد من FCT موجودة في FL.")

        # تحميل النتيجة
        max_len = max(len(missing_in_fct), len(missing_in_fl))
        df_result = pd.DataFrame({
            "Code ناقص في FCT": missing_in_fct + [""] * (max_len - len(missing_in_fct)),
            "Code ناقص في FL": missing_in_fl + [""] * (max_len - len(missing_in_fl))
        })

        st.download_button(
            label="⬇️ تحميل النتيجة Excel",
            data=df_result.to_csv(index=False).encode("utf-8"),
            file_name="codes_comparison_result.csv",
            mime="text/csv"
        )
