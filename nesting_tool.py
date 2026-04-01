import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- 核心排版算法与坐标生成 ---
def calculate_strategies(mat_length, mat_width, piece_l, piece_w):
    strategies = []
    fabric_area = mat_length * mat_width
    piece_area = piece_l * piece_w

    # 方案 1：常规顺向排版 (统一方向，最适合机器连裁)
    cols1 = int(mat_length // piece_l)
    rows1 = int(mat_width // piece_w)
    total1 = cols1 * rows1
    rects1 = [(c * piece_l, r * piece_w, piece_l, piece_w) for r in range(rows1) for c in range(cols1)]
    waste_pct1 = ((fabric_area - (total1 * piece_area)) / fabric_area) * 100
    strategies.append({
        "name": "方案 A：常规顺向排版 (最易裁剪)",
        "total": total1,
        "waste": waste_pct1,
        "rects": rects1,
        "desc": f"方向统一。长度方向排 {cols1} 个，宽度方向排 {rows1} 排。"
    })

    # 方案 2：常规横向排版 (整体旋转90度)
    cols2 = int(mat_length // piece_w)
    rows2 = int(mat_width // piece_l)
    total2 = cols2 * rows2
    rects2 = [(c * piece_w, r * piece_l, piece_w, piece_l) for r in range(rows2) for c in range(cols2)]
    waste_pct2 = ((fabric_area - (total2 * piece_area)) / fabric_area) * 100
    strategies.append({
        "name": "方案 B：常规横向排版 (整体旋转90度)",
        "total": total2,
        "waste": waste_pct2,
        "rects": rects2,
        "desc": f"方向统一。长度方向排 {cols2} 个，宽度方向排 {rows2} 排。"
    })

    # 方案 3：混合交叉排版 (极限省料，但裁剪较慢)
    max_mixed = 0
    best_rects = []
    best_desc = ""
    for i in range(int(mat_width // piece_l) + 1):
        for j in range(int(mat_width // piece_w) + 1):
            if i * piece_l + j * piece_w <= mat_width:
                rects3 = []
                # 区域 1
                for col_i in range(i):
                    for row_i in range(int(mat_length // piece_w)):
                        rects3.append((row_i * piece_w, col_i * piece_l, piece_w, piece_l))
                # 区域 2
                y_offset = i * piece_l
                for col_j in range(j):
                    for row_j in range(int(mat_length // piece_l)):
                        rects3.append((row_j * piece_l, y_offset + col_j * piece_w, piece_l, piece_w))
                if len(rects3) > max_mixed:
                    max_mixed = len(rects3)
                    best_rects = rects3
                    best_desc = f"分为两区：底侧 {i} 排横向，顶侧 {j} 排顺向。"

    waste_pct3 = ((fabric_area - (max_mixed * piece_area)) / fabric_area) * 100
    strategies.append({
        "name": "方案 C：混合交叉排版 (极限省料)",
        "total": max_mixed,
        "waste": waste_pct3,
        "rects": best_rects,
        "desc": best_desc
    })

    # 按产出数量从大到小排序
    strategies.sort(key=lambda x: x['total'], reverse=True)
    return strategies

# --- 绘图函数 ---
def draw_layout(mat_length, mat_width, rects, title):
    # 根据长宽比自动调整画布大小
    ratio = mat_width / mat_length
    fig, ax = plt.subplots(figsize=(10, max(2, 10 * ratio)))
    ax.set_xlim(0, mat_length)
    ax.set_ylim(0, mat_width)
    
    # 画大布料边框 (红色)
    ax.add_patch(patches.Rectangle((0, 0), mat_length, mat_width, fill=False, edgecolor='red', linewidth=3))
    
    # 画小裁片 (蓝色带黑边)
    for (x, y, w, h) in rects:
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=True, facecolor='#add8e6', edgecolor='black', linewidth=1))
    
    ax.set_title(title, fontdict={'family': 'sans-serif'})
    ax.axis('off') # 隐藏坐标轴
    return fig

# --- 单位换算 ---
UNIT_TO_MM = {"毫米 (mm)": 1.0, "厘米 (cm)": 10.0, "米 (m)": 1000.0, "英寸 (inch)": 25.4, "码 (yard)": 914.4}

# --- UI 界面 ---
st.set_page_config(page_title="高级材料排版系统", layout="wide")

st.title("✂️ 高级材料排版系统 (可视化版)")
st.markdown("提供 **3 种排版方案对比**、**废料百分比**，并自动生成**切割排版图**。")
st.divider()

# 输入区域 (使用三列布局更紧凑)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.subheader("📦 布料尺寸")
    mat_len_val = st.number_input("布料长度", value=5.0, step=1.0)
    mat_len_unit = st.selectbox("长度单位", options=list(UNIT_TO_MM.keys()), index=4)
    mat_wid_val = st.number_input("布料门幅宽", value=54.0, step=1.0)
    mat_wid_unit = st.selectbox("宽度单位", options=list(UNIT_TO_MM.keys()), index=3)

with col2:
    st.subheader("🏷️ 裁片尺寸")
    piece_l_val = st.number_input("裁片长度", value=500.0, step=10.0)
    piece_l_unit = st.selectbox("裁片长单位", options=list(UNIT_TO_MM.keys()), index=0)
    piece_w_val = st.number_input("裁片宽度", value=400.0, step=10.0)
    piece_w_unit = st.selectbox("裁片宽单位", options=list(UNIT_TO_MM.keys()), index=0)

with col3:
    st.subheader("⚙️ 操作")
    st.write("请确认左侧尺寸后点击计算：")
    calculate_btn = st.button("🚀 生成排版方案图", use_container_width=True, type="primary")

st.divider()

if calculate_btn:
    # 转换为 mm
    mat_length_mm = mat_len_val * UNIT_TO_MM[mat_len_unit]
    mat_width_mm = mat_wid_val * UNIT_TO_MM[mat_wid_unit]
    piece_l_mm = piece_l_val * UNIT_TO_MM[piece_l_unit]
    piece_w_mm = piece_w_val * UNIT_TO_MM[piece_w_unit]

    if piece_l_mm <= 0 or piece_w_mm <= 0 or mat_length_mm <= 0 or mat_width_mm <= 0:
        st.error("尺寸输入有误，请确保所有数值大于 0！")
    elif piece_l_mm > mat_length_mm and piece_l_mm > mat_width_mm:
        st.error("裁片尺寸过大，当前布料无法排版！")
    else:
        st.caption(f"🔄 实际换算运算尺寸：布料 {mat_length_mm:.1f} x {mat_width_mm:.1f} mm | 裁片 {piece_l_mm:.1f} x {piece_w_mm:.1f} mm")
        
        strategies = calculate_strategies(mat_length_mm, mat_width_mm, piece_l_mm, piece_w_mm)
        
        # 使用 Streamlit 的 Tabs 功能来展示 3 个选项
        tabs = st.tabs([f"🏆 {strategies[0]['name']} (最优)", f"🥈 {strategies[1]['name']}", f"🥉 {strategies[2]['name']}"])
        
        for i, tab in enumerate(tabs):
            strat = strategies[i]
            with tab:
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.metric(label="可裁片数", value=f"{strat['total']} 片")
                    
                    # 废料率颜色判断：大于30%显示红色，否则正常
                    if strat['waste'] > 30:
                        st.error(f"⚠️ 剩余废料率：**{strat['waste']:.2f}%**")
                    else:
                        st.success(f"♻️ 剩余废料率：**{strat['waste']:.2f}%**")
                        
                    st.write(f"**裁剪说明：** {strat['desc']}")
                
                with c2:
                    # 调用 matplotlib 画图并显示
                    fig = draw_layout(mat_length_mm, mat_width_mm, strat['rects'], f"Layout Diagram - {strat['total']} pieces")
                    st.pyplot(fig)