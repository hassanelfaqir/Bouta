import streamlit as st
import pandas as pd
import tabula
import fitz  # PyMuPDF

st.set_page_config(page_title="مقارنة الأكواد بين ملفين PDF", page_icon="🧾")

st.markdown("<h1 style='text-align:center;'>🧾 مقارنة الأكواد بين ملفي الفواتير (FCT / FL)</h1>", unsafe_allow_html=True)

pdf1 = st.file_uploader("📁 الملف الأول (فاتورة FCT)", type="pdf")
pdf2 = st.file_uploader("📁 الملف الثاني (فاتورة FL)", type="pdf")

# -------------------------------
# دالة باش نلقط الأكواد من النص مباشرة
# -------------------------------
import re

def extract_codes_from_text(pdf_file):
    codes = set()
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text = page.get_text("text")
            # نلقط الأكواد اللي فيهم "OSC-" أو "ECHANGE-OSC-" مثلا
            found = re.findall(r"(ECHANGE-?OSC-[0-9\-]+|OSC-[0-9\-]+)", text)
            for f in found:
                codes.add(f.strip().upper())
    return codes


if pdf1 and pdf2:
    try:
        with st.spinner("⏳ جاري قراءة الملفات..."):

            # المحاولة الأولى: نستعمل Tabula
            try:
                df1_list = tabula.read_pdf(pdf1, pages='all', lattice=True)
                df2_list = tabula.read_pdf(pdf2, pages='all', lattice=True)
                df1 = pd.concat(df1_list, ignore_index=True)
                df2 = pd.concat(df2_list, ignore_index=True)

                def detect_code_column(df):
                    for col in df.columns:
                        if "code" in str(col).lower():
                            return col
                    return None

                col_fct = detect_code_column(df1)
                col_fl = detect_code_column(df2)

                if not col_fct or not col_fl:
                    raise ValueError("عمود الكود مش لاقيه")

                codes_fct = set(df1[col_fct].dropna().astype(str).str.strip().str.upper())
                codes_fl = set(df2[col_fl].dropna().astype(str).str.strip().str.upper())

            except Exception:
                # المحاولة الثانية: نستعمل PyMuPDF لاستخراج النصوص
                st.warning("⚠️ فشل استخراج الجداول بـ Tabula، نحاول استخراج الأكواد من النص...")
                pdf1.seek(0)
                pdf2.seek(0)
                codes_fct = extract_codes_from_text(pdf1)
                pdf2.seek(0)
                codes_fl = extract_codes_from_text(pdf2)

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
        df_result = pd.DataFrame({
            "Code ناقص في FCT": missing_in_fct + [""] * (max(len(missing_in_fl), len(missing_in_fct)) - len(missing_in_fct)),
            "Code ناقص في FL": missing_in_fl + [""] * (max(len(missing_in_fl), len(missing_in_fct)) - len(missing_in_fl))
        })

        st.download_button(
            label="⬇️ تحميل النتيجة Excel",
            data=df_result.to_csv(index=False).encode("utf-8"),
            file_name="codes_comparison_result.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ وقع خطأ أثناء القراءة: {e}")
