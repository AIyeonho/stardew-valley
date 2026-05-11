import streamlit as st
import random

st.set_page_config(page_title="농사 게임", page_icon="🌱", layout="centered")

st.title("🌱 작은 농장 게임")
st.write("씨앗을 심고, 물을 주고, 작물을 수확해 돈을 벌어보세요!")

# 게임 상태 저장
if "day" not in st.session_state:
    st.session_state.day = 1
if "money" not in st.session_state:
    st.session_state.money = 100
if "seeds" not in st.session_state:
    st.session_state.seeds = 3
if "crops" not in st.session_state:
    st.session_state.crops = []
if "inventory" not in st.session_state:
    st.session_state.inventory = {"감자": 0}

st.subheader(f"📅 Day {st.session_state.day}")
st.write(f"💰 돈: {st.session_state.money}G")
st.write(f"🌰 씨앗: {st.session_state.seeds}개")
st.write(f"🥔 감자: {st.session_state.inventory['감자']}개")

st.divider()

st.subheader("밭")

# 작물 상태 보여주기
if len(st.session_state.crops) == 0:
    st.write("아직 심은 작물이 없습니다.")
else:
    for i, crop in enumerate(st.session_state.crops):
        if crop["growth"] >= 3:
            st.write(f"{i+1}번 밭: 🥔 수확 가능!")
        else:
            st.write(f"{i+1}번 밭: 🌱 성장도 {crop['growth']}/3")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("씨앗 심기 🌰"):
        if st.session_state.seeds > 0:
            st.session_state.seeds -= 1
            st.session_state.crops.append({"growth": 0})
            st.success("씨앗을 심었습니다!")
        else:
            st.warning("씨앗이 부족합니다.")

with col2:
    if st.button("물 주기 💧"):
        if len(st.session_state.crops) > 0:
            for crop in st.session_state.crops:
                if crop["growth"] < 3:
                    crop["growth"] += 1
            st.success("작물에 물을 줬습니다!")
        else:
            st.warning("물을 줄 작물이 없습니다.")

with col3:
    if st.button("수확하기 🧺"):
        harvested = 0
        new_crops = []

        for crop in st.session_state.crops:
            if crop["growth"] >= 3:
                harvested += 1
            else:
                new_crops.append(crop)

        st.session_state.crops = new_crops
        st.session_state.inventory["감자"] += harvested

        if harvested > 0:
            st.success(f"감자 {harvested}개를 수확했습니다!")
        else:
            st.warning("수확할 작물이 없습니다.")

st.divider()

st.subheader("상점")

col4, col5 = st.columns(2)

with col4:
    if st.button("씨앗 구매 - 20G"):
        if st.session_state.money >= 20:
            st.session_state.money -= 20
            st.session_state.seeds += 1
            st.success("씨앗을 1개 샀습니다.")
        else:
            st.warning("돈이 부족합니다.")

with col5:
    if st.button("감자 판매 + 30G"):
        if st.session_state.inventory["감자"] > 0:
            st.session_state.inventory["감자"] -= 1
            st.session_state.money += 30
            st.success("감자를 팔았습니다.")
        else:
            st.warning("팔 감자가 없습니다.")

st.divider()

if st.button("다음 날로 넘기기 🌙"):
    st.session_state.day += 1
    st.info("다음 날이 되었습니다!")

if st.button("게임 초기화 🔄"):
    st.session_state.clear()
    st.rerun()
