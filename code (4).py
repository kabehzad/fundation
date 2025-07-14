# -*- coding: utf-8 -*-
import streamlit as st
import math
import pandas as pd

# ==============================================================================
# بخش توابع کمکی و محاسباتی
# ==============================================================================

def get_rebar_weight_per_meter(diameter_mm):
    """وزن یک متر میلگرد به کیلوگرم را محاسبه می‌کند."""
    return (diameter_mm ** 2) / 162.0

def calculate_cutting_and_waste(pieces_needed, bar_length=12.0):
    """
    الگوریتم محاسبه تعداد شاخه و لیست پرتی‌ها.
    این تابع یک کپی از لیست را برای کار دریافت می‌کند.
    """
    if not pieces_needed:
        return 0, []

    # کپی کردن لیست برای جلوگیری از تغییر لیست اصلی
    local_pieces = list(pieces_needed)
    local_pieces.sort(reverse=True)
    
    num_bars = 0
    waste_pieces = []
    
    while local_pieces:
        num_bars += 1
        current_bar_length = bar_length
        pieces_to_remove_this_round = []

        for i in range(len(local_pieces)):
            piece = local_pieces[i]
            if current_bar_length >= piece:
                current_bar_length -= piece
                pieces_to_remove_this_round.append(piece)

        # حذف قطعات استفاده شده از لیست اصلی با روشی امن
        temp_list = [p for p in local_pieces if p not in pieces_to_remove_this_round]
        local_pieces = temp_list
        local_pieces.sort(reverse=True)
        
        if current_bar_length > 0.01: # پرتی‌های کمتر از ۱ سانتیمتر
            waste_pieces.append(current_bar_length)
            
    return num_bars, waste_pieces

# ==============================================================================
# شروع طراحی رابط کاربری (UI)
# ==============================================================================

st.set_page_config(layout="wide", page_title="محاسبه‌گر جامع سازه")

st.title("🏗️ محاسبه‌گر جامع مصالح سازه")

# --- منوی انتخاب در نوار کناری ---
page = st.sidebar.radio("یک بخش را برای محاسبه انتخاب کنید:", ["پی گسترده (Raft)", "پی نواری (Strip)"])

# --- تابع برای نمایش نتایج (برای جلوگیری از تکرار کد) ---
def display_results(concrete_volume, rebar_data, concrete_deduction=0):
    st.subheader("📊 نتایج محاسبات")
    
    # بخش بتن
    if concrete_deduction > 0:
        st.success(f"**حجم خالص بتن: {concrete_volume:.2f} متر مکعب** (پس از کسر {concrete_deduction:.2f} متر مکعب حجم میلگرد)")
    else:
        st.success(f"**حجم کل بتن: {concrete_volume:.2f} متر مکعب**")

    # بخش میلگردها
    report_data = []
    all_waste_data = {}
    total_rebar_weight = 0

    for dia, pieces in sorted(rebar_data.items()):
        if not pieces: continue
        total_length = sum(pieces)
        weight = total_length * get_rebar_weight_per_meter(dia)
        total_rebar_weight += weight
        
        num_bars_12m, waste_list = calculate_cutting_and_waste(pieces)
        all_waste_data[dia] = waste_list
        
        report_data.append({
            "نمره میلگرد (mm)": dia,
            "طول کل (m)": f"{total_length:.2f}",
            "وزن کل (kg)": f"{weight:.2f}",
            "تعداد شاخه ۱۲ متری": num_bars_12m
        })

    st.subheader("جدول خلاصه میلگردها")
    st.dataframe(pd.DataFrame(report_data).set_index("نمره میلگرد (mm)"))
    st.info(f"**وزن مجموع کل میلگردها: {total_rebar_weight:.2f} کیلوگرم**")

    # بخش پرتی‌ها
    with st.expander("مشاهده لیست دقیق پرتی‌ها (قطعات باقی‌مانده)"):
        for dia, waste_list in sorted(all_waste_data.items()):
            st.markdown(f"**--- پرتی نمره {dia} ---**")
            if not waste_list:
                st.write("پرتی قابل توجهی وجود ندارد.")
                continue
            
            waste_summary = {}
            for w in waste_list:
                w_rounded = round(w, 2)
                waste_summary[w_rounded] = waste_summary.get(w_rounded, 0) + 1
            
            waste_df_data = [{"طول پرتی (متر)": length, "تعداد قطعه": count} for length, count in sorted(waste_summary.items())]
            st.dataframe(pd.DataFrame(waste_df_data))

# ==============================================================================
# صفحه پی گسترده
# ==============================================================================
if page == "پی گسترده (Raft)":
    # (کد این بخش دست‌نخورده باقی می‌ماند و فقط تابع نمایش نتایج را فراخوانی می‌کند)
    st.header("محاسبه مشخصات پی گسترده")
    with st.form("raft_form"):
        # ... (تمام ورودی‌های پی گسترده که قبلاً داشتیم اینجا قرار می‌گیرند) ...
        col1, col2, col3 = st.columns(3)
        with col1:
            length = st.number_input("طول پی (متر)", min_value=0.1, value=10.0, step=0.5)
            width = st.number_input("عرض پی (متر)", min_value=0.1, value=10.0, step=0.5)
            thickness = st.number_input("ضخامت پی (سانتی‌متر)", min_value=1.0, value=60.0, step=5.0) / 100.0
        
        with col2:
            st.subheader("شبکه پایین (Bottom)")
            bottom_dia = st.selectbox("نمره میلگرد پایین", [8, 10, 12, 14, 16, 18, 20, 22, 25], index=5, key="b_dia")
            bottom_space = st.number_input("فاصله میلگرد پایین (cm)", min_value=1.0, value=15.0, step=1.0) / 100.0
            
            st.subheader("شبکه بالا (Top)")
            top_dia = st.selectbox("نمره میلگرد بالا", [8, 10, 12, 14, 16, 18, 20, 22, 25], index=5, key="t_dia")
            top_space = st.number_input("فاصله میلگرد بالا (cm)", min_value=1.0, value=20.0, step=1.0) / 100.0
        
        with col3:
            cover = st.number_input("کاور بتن (سانتی‌متر)", min_value=1.0, value=7.0, step=0.5) / 100.0
            st.subheader("خرک (Chair)")
            chair_dia = st.selectbox("نمره میلگرد خرک", [8, 10, 12, 14, 16, 18], index=4, key="c_dia")
            chairs_per_sqm = st.number_input("تعداد خرک در هر متر مربع", min_value=0.0, value=1.0, step=0.5)

        submitted = st.form_submit_button("محاسبه پی گسترده")

    if submitted:
        rebar_data = {}
        def calculate_mesh(dia, space, primary_dim, secondary_dim):
            num_bars = math.ceil(((secondary_dim - 2 * cover) / space)) + 1
            hook_length = 0.30
            bar_len_no_overlap = (primary_dim - 2 * cover) + (2 * hook_length)
            overlaps = math.floor(bar_len_no_overlap / 12.0)
            overlap_len = 60 * (dia / 1000.0) if overlaps > 0 else 0
            final_bar_len = bar_len_no_overlap + (overlaps * overlap_len)
            if dia not in rebar_data: rebar_data[dia] = []
            rebar_data[dia].extend([final_bar_len] * num_bars)
        
        calculate_mesh(bottom_dia, bottom_space, length, width)
        calculate_mesh(bottom_dia, bottom_space, width, length)
        calculate_mesh(top_dia, top_space, length, width)
        calculate_mesh(top_dia, top_space, width, length)
        
        num_chairs = math.ceil(length * width * chairs_per_sqm)
        chair_height = thickness - (2*cover) - (bottom_dia/1000.0) - (top_dia/1000.0)
        chair_length = chair_height + 0.80
        if chair_dia not in rebar_data: rebar_data[chair_dia] = []
        rebar_data[chair_dia].extend([chair_length] * num_chairs)
        
        gross_concrete_volume = length * width * thickness
        total_rebar_weight = sum(sum(pieces) * get_rebar_weight_per_meter(dia) for dia, pieces in rebar_data.items())
        rebar_volume = total_rebar_weight / 7850.0
        
        display_results(gross_concrete_volume - rebar_volume, rebar_data, rebar_volume)

# ==============================================================================
# صفحه پی نواری (کامل شده)
# ==============================================================================
elif page == "پی نواری (Strip)":
    st.header("محاسبه مشخصات پی نواری")
    
    st.info("ابتدا اطلاعات عمومی و تعداد آکس‌ها را مشخص کرده و سپس مشخصات هر آکس را در فرم زیر وارد نمایید.")
    
    # ورودی‌های عمومی
    col1, col2 = st.columns(2)
    cover = col1.number_input("کاور بتن (سانتی‌متر)", min_value=1.0, value=5.0, key="strip_cover") / 100.0
    chair_dia = col2.selectbox("نمره میلگرد خرک", [10, 12, 14, 16, 18], index=3, key="strip_chair_dia")

    # تعداد آکس‌ها
    col1, col2 = st.columns(2)
    num_horizontal = col1.number_input("تعداد آکس‌های افقی", min_value=0, max_value=20, value=1, step=1)
    num_vertical = col2.number_input("تعداد آکس‌های عمودی", min_value=0, max_value=20, value=1, step=1)

    with st.form("strip_form"):
        horizontal_axes = []
        vertical_axes = []
        
        # فرم‌های پویا برای آکس‌های افقی
        if num_horizontal > 0:
            st.markdown("---")
            st.subheader("مشخصات آکس‌های افقی")
            for i in range(num_horizontal):
                with st.expander(f"آکس افقی شماره {i+1}", expanded=(i==0)):
                    cols = st.columns(3)
                    axis = {}
                    axis['length'] = cols[0].number_input(f"طول (m)", key=f"h_len_{i}", value=10.0)
                    axis['width'] = cols[1].number_input(f"عرض (m)", key=f"h_wid_{i}", value=1.0)
                    axis['height'] = cols[2].number_input(f"ارتفاع (m)", key=f"h_hei_{i}", value=0.9)
                    cols = st.columns(2)
                    axis['main_rebar_count'] = cols[0].number_input(f"تعداد میلگرد طولی", key=f"h_main_n_{i}", value=18)
                    axis['main_rebar_dia'] = cols[1].selectbox(f"نمره میلگرد طولی", [14,16,18,20], key=f"h_main_d_{i}", index=2)
                    cols = st.columns(3)
                    axis['transverse_type'] = cols[0].selectbox(f"نوع میلگرد عرضی", ["سنجاقی", "خاموت"], key=f"h_trans_t_{i}")
                    axis['transverse_dia'] = cols[1].selectbox(f"نمره میلگرد عرضی", [8,10,12,14], key=f"h_trans_d_{i}", index=1)
                    axis['transverse_spacing'] = cols[2].number_input(f"فاصله عرضی (cm)", key=f"h_trans_s_{i}", value=20.0) / 100.0
                    horizontal_axes.append(axis)
        
        # فرم‌های پویا برای آکس‌های عمودی
        if num_vertical > 0:
            st.markdown("---")
            st.subheader("مشخصات آکس‌های عمودی")
            for i in range(num_vertical):
                with st.expander(f"آکس عمودی شماره {i+1}", expanded=(i==0)):
                    cols = st.columns(3)
                    axis = {}
                    axis['length'] = cols[0].number_input(f"طول (m)", key=f"v_len_{i}", value=14.0)
                    axis['width'] = cols[1].number_input(f"عرض (m)", key=f"v_wid_{i}", value=1.0)
                    axis['height'] = cols[2].number_input(f"ارتفاع (m)", key=f"v_hei_{i}", value=0.9)
                    cols = st.columns(2)
                    axis['main_rebar_count'] = cols[0].number_input(f"تعداد میلگرد طولی", key=f"v_main_n_{i}", value=18)
                    axis['main_rebar_dia'] = cols[1].selectbox(f"نمره میلگرد طولی", [14,16,18,20], key=f"v_main_d_{i}", index=2)
                    cols = st.columns(3)
                    axis['transverse_type'] = cols[0].selectbox(f"نوع میلگرد عرضی", ["سنجاقی", "خاموت"], key=f"v_trans_t_{i}")
                    axis['transverse_dia'] = cols[1].selectbox(f"نمره میلگرد عرضی", [8,10,12,14], key=f"v_trans_d_{i}", index=1)
                    axis['transverse_spacing'] = cols[2].number_input(f"فاصله عرضی (cm)", key=f"v_trans_s_{i}", value=20.0) / 100.0
                    vertical_axes.append(axis)

        submitted = st.form_submit_button("محاسبه پی نواری")

    if submitted:
        rebar_data = {}
        def add_rebar(dia, pieces_list):
            if dia not in rebar_data: rebar_data[dia] = []
            rebar_data[dia].extend(pieces_list)
        
        # محاسبات بتن
        total_vol = sum(ax['length'] * ax['width'] * ax['height'] for ax in horizontal_axes + vertical_axes)
        intersect_vol = sum(h['width'] * v['width'] * max(h['height'], v['height']) for h in horizontal_axes for v in vertical_axes)
        net_concrete_vol = total_vol - intersect_vol
        
        # محاسبات میلگرد
        all_axes = horizontal_axes + vertical_axes
        is_horizontal_list = [True] * len(horizontal_axes) + [False] * len(vertical_axes)
        for i, axis in enumerate(all_axes):
            # ... (بقیه منطق محاسبات که قبلاً داشتیم) ...
            dia = axis['main_rebar_dia']
            base_len = (axis['length'] - 2 * cover) + (2 * 0.30)
            overlaps = math.floor(base_len / 12.0)
            overlap_len = 60 * (dia / 1000.0) if overlaps > 0 else 0
            final_len = base_len + (overlaps * overlap_len)
            add_rebar(dia, [final_len] * axis['main_rebar_count'])
            intersecting_widths = sum(v['width'] for v in vertical_axes) if is_horizontal_list[i] else sum(h['width'] for h in horizontal_axes)
            effective_length = axis['length'] - intersecting_widths
            if effective_length > 0:
                num_pos = math.ceil(effective_length / axis['transverse_spacing'])
                if axis['transverse_type'] == "سنجاقی":
                    p_len = (axis['width'] - 2*cover) + axis['height']
                    add_rebar(axis['transverse_dia'], [p_len] * num_pos * 2)
                else:
                    p_len = 2 * ((axis['width']-2*cover) + (axis['height']-2*cover)) + 0.20
                    add_rebar(axis['transverse_dia'], [p_len] * num_pos)
        
        if all_axes:
            total_axis_length = sum(a['length'] for a in all_axes)
            num_chairs = math.ceil(total_axis_length)
            avg_width = sum(a['width'] for a in all_axes) / len(all_axes)
            avg_height = sum(a['height'] for a in all_axes) / len(all_axes)
            chair_len = avg_width + avg_height + 0.60
            add_rebar(chair_dia, [chair_len] * num_chairs)
            
        display_results(net_concrete_vol, rebar_data)
