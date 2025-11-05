import streamlit as st
import pdfplumber
import pandas as pd
import re

# إعداد الصفحة مع التصميم الاحترافي
st.set_page_config(
    page_title="🧾 مقارنة البيانات بين ملفين PDF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص التصميم مع Buckgrand Pro
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
    }
    
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border-bottom: 3px solid #2E86AB;
    }
    
    .section-header {
        color: #2E86AB;
        font-weight: 600;
        font-size: 1.8rem;
        margin: 1.5rem 0 1rem 0;
        padding-right: 1rem;
        border-right: 4px solid #2E86AB;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #2E86AB;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2E86AB;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #6C757D;
        font-weight: 500;
    }
    
    .uploader-container {
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #2E86AB;
        text-align: center;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #28A745;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #FFF3CD 0%, #FFEAA7 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #FFC107;
        margin: 1rem 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, #F8D7DA 0%, #F5C6CB 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #DC3545;
        margin: 1rem 0;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #2C3E50 0%, #4A235A 100%);
    }
    
    .sidebar-header {
        color: white;
        font-weight: 700;
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    .feature-item {
        color: white;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        border-right: 3px solid #2E86AB;
    }
    
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .diff-cell {
        background-color: #ffcccc !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# الهيدر الرئيسي
st.markdown('<div class="main-header">🧾 نظام مقارنة البيانات بين ملفات PDF</div>', unsafe_allow_html=True)

# رفع الملفات في تصميم جميل
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="uploader-container">', unsafe_allow_html=True)
    st.markdown('<div style="color: #2E86AB; font-weight: 600; font-size: 1.2rem; margin-bottom: 1rem;">📁 الملف الأول (Daryexpress)</div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #6C757D; margin-bottom: 1rem;">الملف الذي يحتوي على Code d\'envoi</div>', unsafe_allow_html=True)
    pdf1 = st.file_uploader(" ", type="pdf", key="pdf1")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="uploader-container">', unsafe_allow_html=True)
    st.markdown('<div style="color: #2E86AB; font-weight: 600; font-size: 1.2rem; margin-bottom: 1rem;">📁 الملف الثاني (OSCARIO)</div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #6C757D; margin-bottom: 1rem;">الملف الذي يحتوي على Code</div>', unsafe_allow_html=True)
    pdf2 = st.file_uploader(" ", type="pdf", key="pdf2")
    st.markdown('</div>', unsafe_allow_html=True)

# الدوال الأساسية (نفس الكود السابق)
def extract_fct_data_complete(pdf_file):
    """استخراج بيانات FCT كاملة مع CRBT"""
    data = {}
    if not pdf_file:
        return data
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if len(row) >= 9:
                            code = str(row[1]).strip()
                            ville = str(row[4]).strip()
                            crbt = str(row[7]).strip()
                            frais = str(row[8]).strip()
                            
                            if code and any(char.isdigit() for char in code) and 'OSC' in code:
                                crbt_clean = re.sub(r'[^\d]', '', crbt)
                                if crbt_clean:
                                    crbt = crbt_clean + " DH"
                                else:
                                    crbt = "0 DH"
                                
                                frais_clean = re.sub(r'[^\d]', '', frais)
                                if frais_clean:
                                    frais = frais_clean + " DH"
                                else:
                                    frais = "غير معروف"
                                
                                data[code] = {
                                    'Ville': ville,
                                    'CRBT': crbt,
                                    'Frais': frais
                                }
    except Exception as e:
        st.error(f"خطأ في استخراج FCT: {e}")
    
    return data

def extract_fl_data_corrected(pdf_file):
    """استخراج بيانات FL مصححة تماماً"""
    data = {}
    if not pdf_file:
        return data
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            lines = full_text.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                code_match = re.search(r'(OSC-\d+-\d+|ECHANGE-OSC-\d+-\d+|REFUND-OSC-\d+-\d+)', line)
                if code_match:
                    code = code_match.group(1)
                    ville = extract_ville_corrected(line, lines, i)
                    crbt, frais = extract_crbt_frais_corrected(line, lines, i)
                    
                    data[code] = {
                        'Ville': ville,
                        'CRBT': crbt,
                        'Frais': frais
                    }
                i += 1
                    
    except Exception as e:
        st.error(f"خطأ في استخراج FL: {e}")
    
    return data

def extract_ville_corrected(line, all_lines, current_index):
    """استخراج المدينة بشكل صحيح"""
    city_patterns = {
        'Casablanca': ['casablanca'],
        'Bouskoura': ['bouskoura'],
        'Mohammedia': ['mohammedia'],
        'Errahma': ['errahma'],
        'Mediouna': ['mediouna'],
        'Tit Mellil': ['tit mellil'],
        'Ain harrouda': ['ain harrouda'],
        'Sidi bennour': ['sidi bennour'],
        'Dar bouazza': ['dar bouazza'],
        'Tamaris': ['tamaris'],
        'Lahraouiyine': ['lahraouiyine'],
         'Rabat': ['rabat', 'الرباط'],
        'Marrakech': ['marrakech', 'مراكش'],
        'Fes': ['fes', 'fez', 'فاس'],
        'Tanger': ['tanger', 'طنجة'],
        'Agadir': ['agadir', 'أكادير']
    }
    
    line_lower = line.lower()
    
    for city, patterns in city_patterns.items():
        for pattern in patterns:
            if pattern in line_lower:
                return city
    
    for offset in [1, 2, -1, -2]:
        idx = current_index + offset
        if 0 <= idx < len(all_lines):
            nearby_line = all_lines[idx].lower()
            for city, patterns in city_patterns.items():
                for pattern in patterns:
                    if pattern in nearby_line:
                        return city
    
    return "غير معروف"

def extract_crbt_frais_corrected(line, all_lines, current_index):
    """استخراج CRBT و Frais معاً بشكل صحيح"""
    crbt = "0 DH"
    frais = "غير معروف"
    
    pattern1 = r'Livré\s+(\d+)\s*DH\s+(\d+)\s*DH'
    match1 = re.search(pattern1, line)
    if match1:
        crbt = match1.group(1) + " DH"
        frais = match1.group(2) + " DH"
        return crbt, frais
    
    pattern2 = r'(\d+)\s*DH\s+(\d+)\s*DH\s*$'
    match2 = re.search(pattern2, line)
    if match2:
        crbt = match2.group(1) + " DH"
        frais = match2.group(2) + " DH"
        return crbt, frais
    
    for offset in [1, 2]:
        idx = current_index + offset
        if idx < len(all_lines):
            next_line = all_lines[idx]
            
            match1_next = re.search(pattern1, next_line)
            if match1_next:
                crbt = match1_next.group(1) + " DH"
                frais = match1_next.group(2) + " DH"
                return crbt, frais
            
            match2_next = re.search(pattern2, next_line)
            if match2_next:
                crbt = match2_next.group(1) + " DH"
                frais = match2_next.group(2) + " DH"
                return crbt, frais
    
    frais_match = re.search(r'(\d+)\s*DH\s*$', line)
    if frais_match:
        frais = frais_match.group(1) + " DH"
    
    for offset in [1, 2]:
        idx = current_index + offset
        if idx < len(all_lines):
            next_line = all_lines[idx]
            frais_match_next = re.search(r'(\d+)\s*DH\s*$', next_line)
            if frais_match_next:
                frais = frais_match_next.group(1) + " DH"
                break
    
    return crbt, frais

def normalize_city_name_final(city_name):
    """توحيد أسماء المدن بشكل نهائي"""
    if not city_name or city_name == "غير معروف":
        return city_name
    
    city_lower = city_name.lower().strip()
    city_lower = re.sub(r'[\n\t]', ' ', city_lower)
    city_lower = re.sub(r'\s+', ' ', city_lower).strip()
    
    city_mapping = {
        'casablanca': 'Casablanca',
        'bouskoura': 'Bouskoura',
        'mohammedia': 'Mohammedia',
        'errahma': 'Errahma',
        'mediouna': 'Mediouna',
        'tit mellil': 'Tit Mellil',
        'ain harrouda': 'Ain harrouda',
        'sidi bennour': 'Sidi bennour',
        'dar bouazza': 'Dar bouazza',
        'tamaris': 'Tamaris',
        'lahraouiyine': 'Lahraouiyine',
        'الدار البيضاء': 'Casablanca',
        'دار البيضاء': 'Casablanca',
        'casa': 'Casablanca',
        'الرباط': 'Rabat',
        'rabat': 'Rabat',
        'مراكش': 'Marrakech',
        'marrakech': 'Marrakech',
        'فاس': 'Fes',
        'fes': 'Fes',
        'fez': 'Fes',
        'طنجة': 'Tanger',
        'tanger': 'Tanger',
        'أكادير': 'Agadir',
        'agadir': 'Agadir',
    }
    
    return city_mapping.get(city_lower, city_name)

def normalize_all_cities(data):
    """توحيد جميع المدن في البيانات"""
    normalized_data = {}
    for code, values in data.items():
        normalized_data[code] = {
            'Ville': normalize_city_name_final(values['Ville']),
            'CRBT': values['CRBT'],
            'Frais': values['Frais']
        }
    return normalized_data

def highlight_differences_in_table(df_differences):
    """إضافة عمود جديد يظهر الاختلافات مع تلوين"""
    highlighted_df = df_differences.copy()
    
    differences_list = []
    
    for _, row in highlighted_df.iterrows():
        diff_items = []
        
        ville_fct_normalized = normalize_city_name_final(str(row['Ville_FCT']))
        ville_fl_normalized = normalize_city_name_final(str(row['Ville_FL']))
        
        if ville_fct_normalized != ville_fl_normalized:
            diff_items.append(f"📍 Ville: {row['Ville_FCT']} ≠ {row['Ville_FL']}")
        
        crbt_fct_clean = re.sub(r'[^\d]', '', str(row['CRBT_FCT']))
        crbt_fl_clean = re.sub(r'[^\d]', '', str(row['CRBT_FL']))
        if crbt_fct_clean != crbt_fl_clean:
            diff_items.append(f"💰 CRBT: {row['CRBT_FCT']} ≠ {row['CRBT_FL']}")
        
        frais_fct_clean = re.sub(r'[^\d]', '', str(row['Frais_FCT']))
        frais_fl_clean = re.sub(r'[^\d]', '', str(row['Frais_FL']))
        if frais_fct_clean != frais_fl_clean:
            diff_items.append(f"💸 Frais: {row['Frais_FCT']} ≠ {row['Frais_FL']}")
        
        differences_list.append(" | ".join(diff_items) if diff_items else "✅ لا توجد اختلافات")
    
    highlighted_df['الاختلافات'] = differences_list
    return highlighted_df

def style_differences_cell_by_cell(df):
    """تلوين الخلايا المختلفة فقط"""
    styles = pd.DataFrame('', index=df.index, columns=df.columns)
    
    for idx, row in df.iterrows():
        ville_fct_normalized = normalize_city_name_final(str(row['Ville_FCT']))
        ville_fl_normalized = normalize_city_name_final(str(row['Ville_FL']))
        
        if ville_fct_normalized != ville_fl_normalized:
            styles.at[idx, 'Ville_FCT'] = 'background-color: #ffcccc; font-weight: 600;'
            styles.at[idx, 'Ville_FL'] = 'background-color: #ffcccc; font-weight: 600;'
        
        crbt_fct_clean = re.sub(r'[^\d]', '', str(row['CRBT_FCT']))
        crbt_fl_clean = re.sub(r'[^\d]', '', str(row['CRBT_FL']))
        if crbt_fct_clean != crbt_fl_clean:
            styles.at[idx, 'CRBT_FCT'] = 'background-color: #ffcccc; font-weight: 600;'
            styles.at[idx, 'CRBT_FL'] = 'background-color: #ffcccc; font-weight: 600;'
        
        frais_fct_clean = re.sub(r'[^\d]', '', str(row['Frais_FCT']))
        frais_fl_clean = re.sub(r'[^\d]', '', str(row['Frais_FL']))
        if frais_fct_clean != frais_fl_clean:
            styles.at[idx, 'Frais_FCT'] = 'background-color: #ffcccc; font-weight: 600;'
            styles.at[idx, 'Frais_FL'] = 'background-color: #ffcccc; font-weight: 600;'
    
    return styles

# المعالجة الرئيسية
if pdf1 and pdf2:
    with st.spinner("⏳ جاري استخراج البيانات من الملفات..."):
        data_fct = extract_fct_data_complete(pdf1)
        data_fl = extract_fl_data_corrected(pdf2)
    
    data_fct = normalize_all_cities(data_fct)
    data_fl = normalize_all_cities(data_fl)
    
    # عرض البيانات المستخرجة
    st.markdown('<div class="section-header">📊 البيانات المستخرجة</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if data_fct:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.success(f"✅ الملف الأول (Daryexpress): {len(data_fct)} سطر")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="color: #2E86AB; font-weight: 600; margin: 1rem 0;">عينة من البيانات المستخرجة:</div>', unsafe_allow_html=True)
            df_fct = pd.DataFrame([
                {
                    'الكود': code, 
                    'المدينة': data_fct[code]['Ville'], 
                    'المبلغ': data_fct[code]['CRBT'],
                    'المصاريف': data_fct[code]['Frais']
                }
                for code in list(data_fct.keys())[:5]
            ])
            st.dataframe(df_fct, use_container_width=True)
        else:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error("❌ لم يتم استخراج بيانات من الملف الأول")
            st.markdown('</div>', unsafe_allow_html=True)
            
    with col2:
        if data_fl:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.success(f"✅ الملف الثاني (OSCARIO): {len(data_fl)} سطر")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="color: #2E86AB; font-weight: 600; margin: 1rem 0;">عينة من البيانات المستخرجة:</div>', unsafe_allow_html=True)
            df_fl = pd.DataFrame([
                {
                    'الكود': code, 
                    'المدينة': data_fl[code]['Ville'],
                    'المبلغ': data_fl[code]['CRBT'],
                    'المصاريف': data_fl[code]['Frais']
                }
                for code in list(data_fl.keys())[:5]
            ])
            st.dataframe(df_fl, use_container_width=True)
        else:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error("❌ لم يتم استخراج بيانات من الملف الثاني")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # المقارنة
    if data_fct and data_fl:
        st.markdown('<div class="section-header">🎯 نتائج المقارنة</div>', unsafe_allow_html=True)
        
        codes_fct = set(data_fct.keys())
        codes_fl = set(data_fl.keys())
        
        missing_in_fct = sorted(codes_fl - codes_fct)
        missing_in_fl = sorted(codes_fct - codes_fl)
        common_codes = codes_fct.intersection(codes_fl)
        
        differences = []
        for code in common_codes:
            ville_fct = data_fct[code]['Ville']
            ville_fl = data_fl[code]['Ville']
            crbt_fct = data_fct[code]['CRBT']
            crbt_fl = data_fl[code]['CRBT']
            frais_fct = data_fct[code]['Frais']
            frais_fl = data_fl[code]['Frais']
            
            crbt_fct_clean = re.sub(r'[^\d]', '', crbt_fct)
            crbt_fl_clean = re.sub(r'[^\d]', '', crbt_fl)
            frais_fct_clean = re.sub(r'[^\d]', '', frais_fct)
            frais_fl_clean = re.sub(r'[^\d]', '', frais_fl)
            
            ville_fct_normalized = normalize_city_name_final(ville_fct)
            ville_fl_normalized = normalize_city_name_final(ville_fl)
            
            ville_different = (ville_fct_normalized != ville_fl_normalized)
            crbt_different = (crbt_fct_clean != crbt_fl_clean)
            frais_different = (frais_fct_clean != frais_fl_clean)
            
            if ville_different or crbt_different or frais_different:
                differences.append({
                    'الكود': code,
                    'مدينة FCT': ville_fct,
                    'مدينة FL': ville_fl,
                    'المبلغ FCT': crbt_fct,
                    'المبلغ FL': crbt_fl,
                    'المصاريف FCT': frais_fct,
                    'المصاريف FL': frais_fl
                })
        
        # عرض النتائج
        if missing_in_fct:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"❌ الأكواد الناقصة في ملف Daryexpress ({len(missing_in_fct)})")
            st.markdown('</div>', unsafe_allow_html=True)
            
            missing_data = []
            for code in missing_in_fct[:10]:  # عرض أول 10 فقط
                if code in data_fl:
                    missing_data.append({
                        'الكود': code,
                        'المدينة': data_fl[code]['Ville'],
                        'المبلغ': data_fl[code]['CRBT'],
                        'المصاريف': data_fl[code]['Frais']
                    })
            if missing_data:
                st.dataframe(pd.DataFrame(missing_data), use_container_width=True)
        
        if missing_in_fl:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"❌ الأكواد الناقصة في ملف FL ({len(missing_in_fl)})")
            st.markdown('</div>', unsafe_allow_html=True)
            
            missing_data = []
            for code in missing_in_fl[:10]:  # عرض أول 10 فقط
                if code in data_fct:
                    missing_data.append({
                        'الكود': code,
                        'المدينة': data_fct[code]['Ville'],
                        'المبلغ': data_fct[code]['CRBT'],
                        'المصاريف': data_fct[code]['Frais']
                    })
            if missing_data:
                st.dataframe(pd.DataFrame(missing_data), use_container_width=True)
        
        if differences:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.warning(f"🔄 الأكواد ذات الاختلافات ({len(differences)})")
            st.markdown('</div>', unsafe_allow_html=True)
            
            df_differences = pd.DataFrame(differences)
            highlighted_df = highlight_differences_in_table(df_differences.rename(columns={
                'الكود': 'Code',
                'مدينة FCT': 'Ville_FCT', 
                'مدينة FL': 'Ville_FL',
                'المبلغ FCT': 'CRBT_FCT',
                'المبلغ FL': 'CRBT_FL',
                'المصاريف FCT': 'Frais_FCT',
                'المصاريف FL': 'Frais_FL'
            }))
            
            styled_df = highlighted_df.style.apply(style_differences_cell_by_cell, axis=None)
            st.dataframe(styled_df, use_container_width=True)
            
            # إحصائيات الاختلافات
            st.markdown('<div class="section-header">📈 إحصائيات الاختلافات</div>', unsafe_allow_html=True)
            
            ville_diff = sum(1 for diff in differences if normalize_city_name_final(diff['مدينة FCT']) != normalize_city_name_final(diff['مدينة FL']))
            crbt_diff = sum(1 for diff in differences if re.sub(r'[^\d]', '', diff['المبلغ FCT']) != re.sub(r'[^\d]', '', diff['المبلغ FL']))
            frais_diff = sum(1 for diff in differences if re.sub(r'[^\d]', '', diff['المصاريف FCT']) != re.sub(r'[^\d]', '', diff['المصاريف FL']))
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">' + str(len(differences)) + '</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">إجمالي الاختلافات</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value" style="color: #DC3545;">' + str(ville_diff) + '</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">📍 اختلافات المدن</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value" style="color: #DC3545;">' + str(crbt_diff) + '</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">💰 اختلافات المبالغ</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value" style="color: #DC3545;">' + str(frais_diff) + '</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">💸 اختلافات المصاريف</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        if not missing_in_fct and not missing_in_fl and not differences:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.success("🎯 جميع البيانات متطابقة بين الملفين!")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # إحصائيات عامة
        st.markdown('<div class="section-header">📊 إحصائيات عامة</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">' + str(len(data_fct)) + '</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">الأكواد في FCT</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">' + str(len(data_fl)) + '</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">الأكواد في FL</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value" style="color: #28A745;">' + str(len(common_codes)) + '</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">الأكواد المشتركة</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value" style="color: #DC3545;">' + str(len(missing_in_fct) + len(missing_in_fl)) + '</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">الأكواد الناقصة</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # تحميل النتائج
        if missing_in_fct or missing_in_fl or differences:
            result_data = []
            
            for code in missing_in_fct:
                if code in data_fl:
                    result_data.append({
                        'الكود': code,
                        'النوع': 'ناقص في Daryexpress',
                        'مدينة FCT': '',
                        'مدينة FL': data_fl[code]['Ville'],
                        'المبلغ FCT': '',
                        'المبلغ FL': data_fl[code]['CRBT'],
                        'المصاريف FCT': '',
                        'المصاريف FL': data_fl[code]['Frais']
                    })
            
            for code in missing_in_fl:
                if code in data_fct:
                    result_data.append({
                        'الكود': code,
                        'النوع': 'ناقص في OSCARIO',
                        'مدينة FCT': data_fct[code]['Ville'],
                        'مدينة FL': '',
                        'المبلغ FCT': data_fct[code]['CRBT'],
                        'المبلغ FL': '',
                        'المصاريف FCT': data_fct[code]['Frais'],
                        'المصاريف FL': ''
                    })
            
            for diff in differences:
                result_data.append({
                    'الكود': diff['الكود'],
                    'النوع': 'اختلاف في البيانات',
                    'مدينة FCT': diff['مدينة FCT'],
                    'مدينة FL': diff['مدينة FL'],
                    'المبلغ FCT': diff['المبلغ FCT'],
                    'المبلغ FL': diff['المبلغ FL'],
                    'المصاريف FCT': diff['المصاريف FCT'],
                    'المصاريف FL': diff['المصاريف FL']
                })
            
            if result_data:
                df_result = pd.DataFrame(result_data)
                csv_data = df_result.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                
                st.markdown("---")
                st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
                st.download_button(
                    label="📥 تحميل نتائج المقارنة كملف Excel",
                    data=csv_data,
                    file_name="نتيجة_المقارنة.csv",
                    mime="text/csv"
                )
                st.markdown('</div>', unsafe_allow_html=True)

