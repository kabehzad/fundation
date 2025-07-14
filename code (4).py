# -*- coding: utf-8 -*-
import streamlit as st
import math
import pandas as pd

# ==============================================================================
# بخش توابع کمکی و محاسباتی (این بخش دقیقاً مانند قبل است)
# ==============================================================================

def get_rebar_weight_per_meter(diameter_mm):
    """وزن یک متر میلگرد به کیلوگرم را بر اساس قطر آن محاسبه می‌کند."""
    return (diameter_mm ** 2) / 162.0

# (می‌توانید توابع دیگر مانند calculate_cutting_and_waste را هم اینجا اضافه کنید)

# ==============================================================================
# بخش طراحی رابط کاربری (UI) و منطق وب اپلیکیشن
# ==============================================================================

st.set_page_config(layout="wide", page_title="محاسبه‌گر مصالح فونداسیون")

st.title("🏗️ محاسبه‌گر مصالح فونداسیون")

# --- منوی انتخاب نوع پی در نوار کناری ---
page = st.sidebar.radio("انتخاب نوع فونداسیون:", ["پی گسترده (Raft)", "پی نواری (Strip)"])

# --- صفحه مربوط به پی گسترده ---
if page == "پی گسترده (Raft)":
    st.header("محاسبه مشخصات پی گسترده")

    with st.form("raft_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            length = st.number_input("طول پی (متر)", min_value=0.1, value=10.0, step=0.5)
            width = st.number_input("عرض پی (متر)", min_value=0.1, value=10.0, step=0.5)
            thickness = st.number_input("ضخامت پی (سانتی‌متر)", min_value=1.0, value=60.0, step=5.0) / 100.0
        
        with col2:
            st.subheader("شبکه پایین (Bottom)")
            bottom_dia = st.selectbox("نمره میلگرد پایین", [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32], index=4)
            bottom_space = st.number_input("فاصله میلگرد پایین (cm)", min_value=1.0, value=15.0, step=1.0) / 100.0
            
            st.subheader("شبکه بالا (Top)")
            top_dia = st.selectbox("نمره میلگرد بالا", [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32], index=4)
            top_space = st.number_input("فاصله میلگرد بالا (cm)", min_value=1.0, value=20.0, step=1.0) / 100.0
        
        with col3:
            cover = st.number_input("کاور بتن (سانتی‌متر)", min_value=1.0, value=7.0, step=0.5) / 100.0
            st.subheader("خرک (Chair)")
            chair_dia = st.selectbox("نمره میلگرد خرک", [8, 10, 12, 14, 16, 18], index=4)
            chairs_per_sqm = st.number_input("تعداد خرک در هر متر مربع", min_value=0.0, value=1.0, step=0.5)

        submitted = st.form_submit_button("محاسبه کن")

    if submitted:
        rebar_pieces = {}

        def calculate_mesh(dia, space, primary_dim, secondary_dim):
            num_bars = math.ceil(((secondary_dim - 2 * cover) / space)) + 1
            hook_length = 0.30
            bar_len_no_overlap = (primary_dim - 2 * cover) + (2 * hook_length)
            overlaps = math.floor(bar_len_no_overlap / 12.0)
            overlap_len = 60 * (dia / 1000.0) if overlaps > 0 else 0
            final_bar_len = bar_len_no_overlap + (overlaps * overlap_len)
            return [final_bar_len] * num_bars
        
        # افزودن میلگردها به لیست
        rebar_pieces[bottom_dia] = calculate_mesh(bottom_dia, bottom_space, length, width) + calculate_mesh(bottom_dia, bottom_space, width, length)
        rebar_pieces[top_dia] = rebar_pieces.get(top_dia, []) + calculate_mesh(top_dia, top_space, length, width) + calculate_mesh(top_dia, top_space, width, length)
        
        # محاسبه خرک
        num_chairs = math.ceil(length * width * chairs_per_sqm)
        chair_height = thickness - (2*cover) - (bottom_dia/1000.0) - (top_dia/1000.0)
        chair_length = chair_height + 0.80
        rebar_pieces[chair_dia] = rebar_pieces.get(chair_dia, []) + [chair_length] * num_chairs

        # --- نمایش نتایج ---
        st.subheader("📊 نتایج محاسبات")

        # ۱. بتن
        gross_concrete_volume = length * width * thickness
        total_rebar_weight = sum(sum(pieces) * get_rebar_weight_per_meter(dia) for dia, pieces in rebar_pieces.items())
        rebar_volume = total_rebar_weight / 7850.0
        net_concrete_volume = gross_concrete_volume - rebar_volume

        st.success(f"**حجم خالص بتن مورد نیاز: {net_concrete_volume:.2f} متر مکعب**")

        # ۲. میلگردها
        report_data = []
        for dia, pieces in sorted(rebar_pieces.items()):
            total_length = sum(pieces)
            total_weight = total_length * get_rebar_weight_per_meter(dia)
            num_bars_12m = math.ceil(total_length / 12.0)
            report_data.append({
                "نمره میلگرد (mm)": dia,
                "طول کل (m)": f"{total_length:.2f}",
                "وزن کل (kg)": f"{total_weight:.2f}",
                "تعداد شاخه ۱۲ متری": num_bars_12m
            })
        
        df = pd.DataFrame(report_data)
        st.dataframe(df)
        st.info(f"**وزن مجموع کل میلگردها: {total_rebar_weight:.2f} کیلوگرم**")

# --- صفحه مربوط به پی نواری (ساده شده برای وب) ---
elif page == "پی نواری (Strip)":
    st.header("محاسبه مشخصات پی نواری")
    st.warning("این بخش در حال توسعه است و محاسبات آن ساده‌سازی شده است.")
    # پیاده‌سازی کامل این بخش در وب نیازمند مدیریت حالت (Session State) برای افزودن/حذف
    # داینامیک آکس‌ها است که کمی پیشرفته‌تر است.
    # در اینجا یک مثال برای یک نوار تکی آورده شده است.

    with st.form("strip_form"):
        length = st.number_input("طول نوار (متر)", min_value=0.1, value=10.0)
        width = st.number_input("عرض نوار (متر)", min_value=0.1, value=1.0)
        height = st.number_input("ارتفاع نوار (متر)", min_value=0.1, value=0.9)
        cover = st.number_input("کاور (سانتی‌متر)", min_value=1.0, value=5.0) / 100.0

        main_rebar_dia = st.selectbox("نمره میلگرد طولی", [12, 14, 16, 18, 20], index=3)
        main_rebar_count = st.number_input("تعداد میلگرد طولی", min_value=1, value=18)
        
        transverse_dia = st.selectbox("نمره میلگرد عرضی (سنجاقی)", [8, 10, 12, 14], index=1)
        transverse_spacing = st.number_input("فاصله سنجاقی (سانتی‌متر)", min_value=1.0, value=20.0) / 100.0

        submitted = st.form_submit_button("محاسبه کن")

    if submitted:
        # محاسبات ساده شده برای یک نوار
        concrete_vol = length * width * height
        
        # میلگرد طولی
        hook_length = 0.30
        base_len = (length - 2 * cover) + (2 * hook_length)
        total_long_rebar = base_len * main_rebar_count
        weight_long = total_long_rebar * get_rebar_weight_per_meter(main_rebar_dia)

        # میلگرد عرضی (سنجاقی)
        num_transverse = math.ceil(length / transverse_spacing) * 2 # دو عدد بالا و پایین
        len_transverse = (width - 2*cover) + height
        total_trans_rebar = num_transverse * len_transverse
        weight_trans = total_trans_rebar * get_rebar_weight_per_meter(transverse_dia)

        st.subheader("📊 نتایج محاسبات برای یک نوار")
        st.success(f"**حجم بتن مورد نیاز: {concrete_vol:.2f} متر مکعب**")
        st.info(f"**وزن کل میلگرد طولی (نمره {main_rebar_dia}): {weight_long:.2f} کیلوگرم**")
        st.info(f"**وزن کل میلگرد عرضی (نمره {transverse_dia}): {weight_trans:.2f} کیلوگرم**")