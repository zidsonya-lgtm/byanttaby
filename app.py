
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

إعدادات الصفحة

st.set_page_config(
page_title="نظام إدارة المخزون الطبي",
page_icon="🏥",
layout="wide",
initial_sidebar_state="expanded"
)

RTL Support with Custom CSS

st.markdown("""
<style>
.main {direction: rtl; text-align: right;}
.stDataFrame {direction: rtl;}
.metric-card {
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
padding: 20px;
border-radius: 10px;
color: white;
text-align: center;
margin: 10px 0;
}
.alert-high {background: #ff6b6b; color: white; padding: 10px; border-radius: 5px;}
.alert-medium {background: #ffa502; color: white; padding: 10px; border-radius: 5px;}
.alert-ok {background: #2ed573; color: white; padding: 10px; border-radius: 5px;}
h1, h2, h3 {text-align: right;}
</style>
""", unsafe_allow_html=True)

==================== دوال المعالجة ====================

@st.cache_data
def load_medical_data(file):
"""تحميل ومعالجة بيانات التقرير الطبي"""
try:
df = pd.read_excel(file, sheet_name=0, header=2)
return df
except:
return None

def calculate_inventory_status(received_df, distributed_df):
"""حالة المخزون: مقارنة المستلم مع المصروف"""
inventory = received_df.copy()
# دمج بيانات الصرف
if distributed_df is not None:
inventory = inventory.merge(
distributed_df.groupby('اسم الصنف')['الكمية'].sum().reset_index(),
on='اسم الصنف', how='left', suffixes=('_مستلم', '_مصروف')
)
inventory['الرصيد'] = inventory['الكمية_مستلم'] - inventory['الكمية_مصروف'].fillna(0)
inventory['نسبة_الصرف'] = (inventory['الكمية_مصروف'].fillna(0) / inventory['الكمية_مستلم'] * 100).round(1)
inventory['الحالة'] = inventory.apply(
lambda x: 'ناقص ⚠️' if x['الرصيد'] < 0 else
'منخفض 🔶' if x['نسبة_الصرف'] > 80 else
'متوفر ✅', axis=1
)

return inventory

def generate_shortage_report(inventory_df):
"""توليد تقرير الأصناف الناقصة"""
shortage = inventory_df[
(inventory_df['الحالة'].str.contains('ناقص|منخفض', na=False)) |
(inventory_df['الرصيد'] < 0)
].copy()

shortage['الأولوية'] = shortage.apply(  
    lambda x: 'عالية 🔴' if x['الرصيد'] < 0 else   
             'متوسطة 🟡' if x['نسبة_الصرف'] > 80 else 'منخفضة 🟢',  
    axis=1  
)  
  
return shortage.sort_values('الرصيد')

==================== الواجهة الرئيسية ====================

def main():
# الشريط الجانبي
with st.sidebar:
st.image("🏥", width=80)
st.title("⚙️ لوحة التحكم")

uploaded_file = st.file_uploader(  
        "📁 رفع ملف التقرير",  
        type=['xlsx', 'xls'],  
        help="ارفع ملف إكسل يحتوي على بيانات المخزون"  
    )  
      
    st.divider()  
      
    # قائمة التنقل  
    page = st.radio(  
        "📊 التنقل بين الأقسام",            ["🏠 الرئيسية", "📦 المخزون", "⚠️ النواقص", "📈 التحليلات", "📤 التصدير"],  
        label_visibility="collapsed"  
    )  
      
    st.divider()  
    st.info(f"📅 تاريخ اليوم: {datetime.now().strftime('%Y-%m-%d')}")  
    st.caption("نظام إدارة المخزون الطبي - وحدة الإمداد الطبي")  

# ==================== الصفحة الرئيسية ====================  
if page == "🏠 الرئيسية":  
    st.title("🏥 التقرير الشامل للأدوية والمستلزمات الطبية")  
    st.markdown("---")  
      
    if uploaded_file:  
        # عرض المؤشرات الرئيسية  
        col1, col2, col3, col4 = st.columns(4)  
          
        with col1:  
            st.metric("📦 إجمالي الأصناف", "51", "من بئر أحمد")  
        with col2:  
            st.metric("📤 إجمالي المصروف", "47", "لنقطتي التوزيع")  
        with col3:  
            st.metric("✅ الأصناف المتوفرة", "45", "92%")  
        with col4:  
            st.metric("⚠️ الأصناف الناقصة", "4", "تحتاج إمداد", delta_color="inverse")  
          
        st.markdown("---")  
          
        # رسوم بيانية سريعة  
        col_chart1, col_chart2 = st.columns(2)  
          
        with col_chart1:  
            st.subheader("📊 توزيع الأصناف حسب الفئة")  
            # بيانات تجريبية للعرض  
            categories = {  
                'الفئة': ['مستلزمات طبية', 'محاليل وريدية', 'مضادات حيوية',   
                         'مسكنات', 'أدوية عامة', 'جهاز هضمي', 'فيتامينات'],  
                'العدد': [15, 7, 7, 6, 6, 5, 3]  
            }  
            fig_pie = px.pie(  
                names=categories['الفئة'],   
                values=categories['عدد'],  
                color_discrete_sequence=px.colors.sequential.RdBu,  
                hole=0.4  
            )  
            fig_pie.update_layout(showlegend=True, height=400)  
            st.plotly_chart(fig_pie, use_container_width=True)  
          
        with col_chart2:  
            st.subheader("📍 توزيع الصرف حسب النقاط")                distribution_data = pd.DataFrame({  
                'نقطة التوزيع': ['الرباط (الكتيبة 1)', 'التواهي (الكتيبة 2)'],  
                'عدد الأصناف': [31, 21],  
                'النسبة': [59.6, 40.4]  
            })  
            fig_bar = px.bar(  
                distribution_data,   
                x='نقطة التوزيع',   
                y='عدد الأصناف',  
                color='النسبة',  
                text='النسبة',  
                color_continuous_scale='Viridis'  
            )  
            fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')  
            fig_bar.update_layout(height=400, showlegend=False)  
            st.plotly_chart(fig_bar, use_container_width=True)  
          
        # جدول النواقص العاجلة  
        st.subheader("🚨 تنبيهات عاجلة - الأصناف الناقصة")  
        shortage_preview = pd.DataFrame({  
            'الصنف': ['DNS (محلول وريدي)', 'R/L (رينجر لاكتات)', 'Sterile Gauze', 'Brufen Tab'],  
            'المستلم': [1, 1, 2, 1],  
            'المصروف': [5, 5, 5, 2],  
            'النقص': [-4, -4, -3, -1],  
            'الأولوية': ['🔴 عالية', '🔴 عالية', '🔴 عالية', '🟡 متوسطة']  
        })  
          
        def color_status(val):  
            if 'عالية' in str(val):  
                return 'background-color: #ff6b6b; color: white'  
            elif 'متوسطة' in str(val):  
                return 'background-color: #ffa502; color: white'  
            return ''  
          
        st.dataframe(  
            shortage_preview.style.applymap(color_status, subset=['الأولوية']),  
            use_container_width=True,  
            hide_index=True  
        )  
          
    else:  
        st.info("📤 يرجى رفع ملف التقرير للبدء في التحليل")  
        st.markdown("""  
        ### 📋 خطوات الاستخدام:  
        1. اضغط على **📁 رفع ملف التقرير** في الشريط الجانبي  
        2. اختر ملف الإكسل الخاص بالمخزون  
        3. انتقل بين الأقسام باستخدام القائمة الجانبية  
        4. استعرض التقارير والرسوم البيانية  
        5. صدّر النتائج عند الحاجة  
        """)  
# ==================== صفحة المخزون ====================  
elif page == "📦 المخزون":  
    st.title("📦 إدارة المخزون التفصيلي")  
      
    if uploaded_file:  
        # فلاتر البحث  
        col_filter1, col_filter2, col_filter3 = st.columns(3)  
          
        with col_filter1:  
            category_filter = st.multiselect(  
                "🔍 تصفية حسب الفئة",  
                ['محاليل وريدية', 'مضادات حيوية', 'مسكنات', 'جهاز هضمي',   
                 'فيتامينات', 'أدوية عامة', 'مستلزمات طبية']  
            )  
          
        with col_filter2:  
            status_filter = st.multiselect(  
                "📊 حالة الصنف",  
                ['متوفر ✅', 'منخفض 🔶', 'ناقص ⚠️']  
            )  
          
        with col_filter3:  
            search_term = st.text_input("🔎 بحث باسم الصنف")  
          
        # جدول المخزون (بيانات تجريبية للعرض)  
        inventory_data = []  
        for i in range(1, 50):  
            inventory_data.append({  
                'م': i,  
                'اسم الصنف': f'صنف طبي {i}',  
                'الكمية': 10,  
                'الوحدة': 'باكت',  
                'الفئة': 'مضادات حيوية',  
                'القائمة': 'قائمة 1',  
                'الحالة': 'متوفر ✅',  
                'الرصيد': 8,  
                'نسبة الصرف': '20%'  
            })  
          
        df_inventory = pd.DataFrame(inventory_data)  
          
        # تطبيق الفلاتر  
        if category_filter:  
            df_inventory = df_inventory[df_inventory['الفئة'].isin(category_filter)]  
        if search_term:  
            df_inventory = df_inventory[df_inventory['اسم الصنف'].str.contains(search_term, case=False)]  
          
        st.dataframe(  
            df_inventory,                use_container_width=True,  
            column_config={  
                "الحالة": st.column_config.TextColumn("الحالة", help="حالة توفر الصنف"),  
                "الرصيد": st.column_config.NumberColumn("الرصيد", format="%d"),  
                "نسبة الصرف": st.column_config.TextColumn("نسبة الصرف")  
            }  
        )  
          
        # زر تصدير  
        if st.button("📥 تصدير جدول المخزون"):  
            buffer = io.BytesIO()  
            df_inventory.to_excel(buffer, index=False, engine='openpyxl')  
            st.download_button(  
                label="💾 تحميل Excel",  
                data=buffer.getvalue(),  
                file_name=f"inventory_{datetime.now().strftime('%Y%m%d')}.xlsx",  
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  
            )  
              
    else:  
        st.warning("⚠️ يرجى رفع الملف أولاً من الصفحة الرئيسية")  

# ==================== صفحة النواقص ====================  
elif page == "⚠️ النواقص":  
    st.title("⚠️ تقرير الأصناف الناقصة")  
    st.markdown("🔴 الأصناف التي تحتاج إعادة إمداد عاجل")  
      
    if uploaded_file:  
        # بطاقات النواقص  
        shortage_items = [  
            {'الصنف': 'DNS (محلول وريدي)', 'النقص': 4, 'الأولوية': 'عالية', 'التوصية': 'طلب فوري من بئر أحمد'},  
            {'الصنف': 'R/L (رينجر لاكتات)', 'النقص': 4, 'الأولوية': 'عالية', 'التوصية': 'طلب فوري من بئر أحمد'},  
            {'الصنف': 'Sterile Gauze', 'النقص': 3, 'الأولوية': 'عالية', 'التوصية': 'زيادة المخزون الاحتياطي'},  
            {'الصنف': 'Brufen Tab', 'النقص': 1, 'الأولوية': 'متوسطة', 'التوضية': 'مراجعة كميات الصرف'}  
        ]  
          
        for item in shortage_items:  
            priority_color = "alert-high" if item['الأولوية'] == 'عالية' else "alert-medium"  
            with st.container():  
                st.markdown(f"""  
                <div class="{priority_color}">  
                    <strong>📦 {item['الصنف']}</strong><br>  
                    النقص: {item['النقص']} وحدة | الأولوية: {item['الأولوية']} |   
                    التوصية: {item['التوصية']}  
                </div>  
                """, unsafe_allow_html=True)  
          
        st.markdown("---")  
          
        # توصيات النظام            st.subheader("💡 توصيات النظام")  
        recommendations = [  
            "✅ مراجعة عاجلة لعمليات الصرف وضبط الكميات المسموح بها",  
            "✅ توحيد نظام التسجيل في جميع نقاط التوزيع",  
            "✅ إعادة إمداد الأصناف الناقصة فوراً من المصدر",  
            "✅ إنشاء نظام مراقبة للمخزون بشكل دوري (أسبوعي)",  
            "✅ تفعيل نظام تنبيهات تلقائي عند وصول الصنف للحد الأدنى"  
        ]  
          
        for rec in recommendations:  
            st.markdown(f"- {rec}")  
              
    else:  
        st.info("📤 ارفع الملف لعرض تقرير النواقص")  

# ==================== صفحة التحليلات ====================  
elif page == "📈 التحليلات":  
    st.title("📈 التحليلات الإحصائية")  
      
    if uploaded_file:  
        tab1, tab2, tab3 = st.tabs(["📊 الرسوم البيانية", "📋 الإحصائيات", "🔍 التحليل المتقدم"])  
          
        with tab1:  
            col1, col2 = st.columns(2)  
              
            with col1:  
                st.subheader("نسبة الصرف حسب الفئة")  
                category_stats = pd.DataFrame({  
                    'الفئة': ['محاليل', 'مضادات', 'مسكنات', 'هضمي', 'فيتامينات', 'عامة', 'مستلزمات'],  
                    'نسبة_الصرف': [24, 6, 36, 38, 60, 52, 21]  
                })  
                fig1 = px.bar(  
                    category_stats, x='الفئة', y='نسبة_الصرف',  
                    color='نسبة_الصرف', text='نسبة_الصرف',  
                    color_continuous_scale='RdYlGn_r'  
                )  
                fig1.update_traces(texttemplate='%{text}%', textposition='outside')  
                fig1.update_layout(xaxis_tickangle=-45, height=400)  
                st.plotly_chart(fig1, use_container_width=True)  
              
            with col2:  
                st.subheader("حالة الأصناف")  
                status_data = pd.DataFrame({  
                    'الحالة': ['لم يصرف', 'صرف جزئي', 'صرف كامل'],  
                    'العدد': [30, 15, 4]  
                })  
                fig2 = px.donut(  
                    status_data, names='الحالة', values='العدد',  
                    color='الحالة', hole=0.5  
                )                    fig2.update_layout(showlegend=True, height=400)  
                st.plotly_chart(fig2, use_container_width=True)  
          
        with tab2:  
            st.subheader("📋 ملخص الإحصائيات")  
            stats_col1, stats_col2, stats_col3 = st.columns(3)  
              
            with stats_col1:  
                st.metric("إجمالي الكميات المستلمة", "243", "وحدة")  
                st.metric("إجمالي الكميات المصروفة", "47", "وحدة")  
                st.metric("متوسط نسبة الصرف", "19.3%", "-5.2%")  
              
            with stats_col2:  
                st.metric("أعلى فئة صرفاً", "أدوية عامة", "52%")  
                st.metric("أقل فئة صرفاً", "مضادات حيوية", "6%")  
                st.metric("نسبة التغطية", "92%", "✅ ممتاز")  
              
            with stats_col3:  
                st.metric("نقاط التوزيع", "2", "الرباط + التواهي")  
                st.metric("تاريخ آخر تحديث", "10 أبريل 2026", "")  
                st.metric("مصدر الإمداد", "بئر أحمد", "")  
          
        with tab3:  
            st.subheader("🔍 تحليل الاتجاهات")  
            st.info("💡 هذه الميزة تتطلب بيانات تاريخية متعددة الفترات")  
              
            # محاكاة لتحليل الاتجاه  
            trend_data = pd.DataFrame({  
                'التاريخ': pd.date_range('2026-04-01', periods=10),  
                'المستلم': [45, 48, 52, 49, 51, 53, 50, 52, 51, 49],  
                'المصروف': [35, 38, 42, 40, 45, 43, 41, 47, 46, 44]  
            })  
              
            fig_trend = px.line(  
                trend_data, x='التاريخ',   
                y=['المستلم', 'المصروف'],  
                markers=True,  
                title='اتجاهات المخزون خلال 10 أيام',  
                labels={'value': 'الكمية', 'variable': 'النوع'}  
            )  
            st.plotly_chart(fig_trend, use_container_width=True)  
              
    else:  
        st.info("📤 ارفع الملف لعرض التحليلات")  

# ==================== صفحة التصدير ====================  
elif page == "📤 التصدير":  
    st.title("📤 تصدير التقارير")  
      
    if uploaded_file:            st.markdown("### اختر نوع التقرير المطلوب تصديره:")  
          
        report_type = st.radio(  
            "نوع التقرير",  
            ["📋 تقرير المخزون الكامل", "⚠️ تقرير النواقص العاجلة",   
             "📊 تقرير التحليلات الإحصائية", "🗂️ جميع التقارير (ZIP)"],  
            horizontal=True  
        )  
          
        format_type = st.selectbox(  
            "صيغة الملف",  
            ["Excel (.xlsx)", "PDF (.pdf)", "CSV (.csv)"]  
        )  
          
        if st.button("🔄 توليد التقرير", type="primary"):  
            with st.spinner("جاري تحضير التقرير..."):  
                # محاكاة عملية التصدير  
                st.success("✅ تم تجهيز التقرير بنجاح!")  
                  
                # زر التحميل  
                buffer = io.BytesIO()  
                pd.DataFrame({'تجربة': ['بيانات التقرير']}).to_excel(buffer, index=False)  
                  
                st.download_button(  
                    label="💾 تحميل التقرير الآن",  
                    data=buffer.getvalue(),  
                    file_name=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M')}.{format_type.split('(')[1].replace(')', '')}",  
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  
                )  
          
        st.markdown("---")  
        st.markdown("""  
        ### ⚙️ خيارات متقدمة:  
        - [ ] تضمين الرسوم البيانية في التقرير  
        - [ ] إضافة شعار المؤسسة  
        - [ ] تشفير الملف بكلمة مرور  
        - [ ] جدولة إرسال التقرير تلقائياً  
        """)  
          
    else:  
        st.warning("⚠️ يرجى رفع الملف أولاً")

تشغيل التطبيق

if name == "main":
main()
