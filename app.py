import streamlit as st
import random

st.set_page_config(
    page_title="작은 농장 게임",
    page_icon="🌾",
    layout="centered"
)

# -----------------------------
# 작물 데이터
# -----------------------------
CROPS = {
    "감자": {
        "seed_price": 40,
        "sell_price": 50,
        "grow_days": 5,
        "harvest_min": 2,
        "harvest_max": 4,
        "emoji": "🥔",
        "stages": ["🟫", "🌱", "🌿", "🌾", "🥔"]
    },
    "옥수수": {
        "seed_price": 120,
        "sell_price": 150,
        "grow_days": 12,
        "harvest_min": 2,
        "harvest_max": 3,
        "emoji": "🌽",
        "stages": ["🟫", "🌱", "🌿", "🎋", "🌽"]
    },
    "딸기": {
        "seed_price": 80,
        "sell_price": 200,
        "grow_days": 8,
        "harvest_min": 1,
        "harvest_max": 1,
        "emoji": "🍓",
        "stages": ["🟫", "🌱", "🌿", "🌸", "🍓"]
    },
    "호박": {
        "seed_price": 200,
        "sell_price": 450,
        "grow_days": 12,
        "harvest_min": 1,
        "harvest_max": 1,
        "emoji": "🎃",
        "stages": ["🟫", "🌱", "🌿", "🍃", "🎃"]
    }
}

GRADE_DATA = {
    "일반": {
        "chance": 70,
        "multiplier": 1.0,
        "mark": ""
    },
    "은별": {
        "chance": 20,
        "multiplier": 1.5,
        "mark": "⭐"
    },
    "금별": {
        "chance": 10,
        "multiplier": 2.0,
        "mark": "🌟"
    }
}

HOTBAR_SIZE = 9
FIELD_SIZE = 5


# -----------------------------
# 기본 함수
# -----------------------------
def choose_grade():
    roll = random.randint(1, 100)

    if roll <= 70:
        return "일반"
    elif roll <= 90:
        return "은별"
    else:
        return "금별"


def empty_tile():
    return {
        "crop": None,
        "age": 0,
        "watered": False
    }


def empty_slot():
    return {
        "item_type": None,
        "name": None,
        "grade": None,
        "count": 0
    }


def make_item(item_type, name, count, grade=None):
    return {
        "item_type": item_type,
        "name": name,
        "grade": grade,
        "count": count
    }


def item_label(slot):
    if slot["count"] <= 0:
        return "비어있음"

    if slot["item_type"] == "seed":
        return f"{CROPS[slot['name']]['emoji']} {slot['name']} 씨앗 x{slot['count']}"

    if slot["item_type"] == "crop":
        grade = slot["grade"]
        mark = GRADE_DATA[grade]["mark"]
        return f"{CROPS[slot['name']]['emoji']} {slot['name']} {mark} x{slot['count']}"

    return "알 수 없음"


def can_stack(a, b):
    return (
        a["item_type"] == b["item_type"]
        and a["name"] == b["name"]
        and a["grade"] == b["grade"]
    )


def add_to_inventory(new_item):
    """
    9칸 핫바에 아이템 추가
    같은 아이템은 겹쳐짐
    빈칸이 없으면 False 반환
    """
    if new_item["count"] <= 0:
        return True

    # 기존 슬롯에 합치기
    for slot in st.session_state.hotbar:
        if slot["count"] > 0 and can_stack(slot, new_item):
            slot["count"] += new_item["count"]
            return True

    # 빈칸에 넣기
    for i in range(HOTBAR_SIZE):
        if st.session_state.hotbar[i]["count"] <= 0:
            st.session_state.hotbar[i] = new_item
            return True

    return False


def remove_one_from_slot(index):
    slot = st.session_state.hotbar[index]
    slot["count"] -= 1

    if slot["count"] <= 0:
        st.session_state.hotbar[index] = empty_slot()


def get_crop_stage(tile):
    crop_name = tile["crop"]

    if crop_name is None:
        return "⬜"

    crop = CROPS[crop_name]
    grow_days = crop["grow_days"]
    age = tile["age"]

    if age >= grow_days:
        return crop["stages"][-1]

    progress = age / grow_days

    if progress < 0.25:
        return crop["stages"][0]
    elif progress < 0.5:
        return crop["stages"][1]
    elif progress < 0.75:
        return crop["stages"][2]
    else:
        return crop["stages"][3]


def is_fully_grown(tile):
    if tile["crop"] is None:
        return False

    return tile["age"] >= CROPS[tile["crop"]]["grow_days"]


# -----------------------------
# 게임 초기화
# -----------------------------
def reset_game():
    st.session_state.day = 1
    st.session_state.money = 500
    st.session_state.selected_slot = 0

    st.session_state.field = [
        [empty_tile() for _ in range(FIELD_SIZE)]
        for _ in range(FIELD_SIZE)
    ]

    st.session_state.hotbar = [empty_slot() for _ in range(HOTBAR_SIZE)]

    # 시작 아이템
    st.session_state.hotbar[0] = make_item("seed", "감자", 5)
    st.session_state.hotbar[1] = make_item("seed", "딸기", 2)


if "day" not in st.session_state:
    reset_game()


# -----------------------------
# 화면 제목
# -----------------------------
st.title("🌾 작은 농장 게임")
st.write("5x5 밭에 씨앗을 심고, 물을 주고, 수확해서 돈을 벌어보세요.")

st.info(
    "사용법: 아래 핫바에서 씨앗 슬롯을 선택한 뒤, 밭의 빈칸을 누르면 심을 수 있습니다. "
    "작물은 물을 준 날만 성장합니다."
)

# -----------------------------
# 상태 표시
# -----------------------------
col_status_1, col_status_2, col_status_3 = st.columns(3)

with col_status_1:
    st.metric("📅 날짜", f"{st.session_state.day}일")

with col_status_2:
    st.metric("💰 돈", f"{st.session_state.money}원")

with col_status_3:
    selected = st.session_state.hotbar[st.session_state.selected_slot]
    st.metric("🎒 선택 슬롯", f"{st.session_state.selected_slot + 1}번")


st.divider()


# -----------------------------
# 핫바 선택
# -----------------------------
st.subheader("🎒 핫바 / 인벤토리")

hotbar_cols = st.columns(HOTBAR_SIZE)

for i in range(HOTBAR_SIZE):
    slot = st.session_state.hotbar[i]
    label = item_label(slot)

    button_text = f"{i + 1}\n{label}"

    if i == st.session_state.selected_slot:
        button_text = f"✅ {button_text}"

    with hotbar_cols[i]:
        if st.button(button_text, key=f"slot_{i}", use_container_width=True):
            st.session_state.selected_slot = i
            st.rerun()


selected_slot = st.session_state.hotbar[st.session_state.selected_slot]

if selected_slot["count"] > 0:
    st.write(f"현재 선택: **{item_label(selected_slot)}**")
else:
    st.write("현재 선택: **비어있음**")


st.divider()


# -----------------------------
# 밭
# -----------------------------
st.subheader("🌱 5x5 밭")

for r in range(FIELD_SIZE):
    cols = st.columns(FIELD_SIZE)

    for c in range(FIELD_SIZE):
        tile = st.session_state.field[r][c]

        crop_icon = get_crop_stage(tile)

        if tile["crop"] is None:
            button_text = "⬜\n빈 밭"
        else:
            crop_name = tile["crop"]
            crop_data = CROPS[crop_name]

            if is_fully_grown(tile):
                button_text = f"{crop_icon}\n{crop_name} 수확!"
            else:
                water_text = "💧" if tile["watered"] else "마름"
                button_text = f"{crop_icon}\n{crop_name} {tile['age']}/{crop_data['grow_days']}\n{water_text}"

        with cols[c]:
            if st.button(button_text, key=f"field_{r}_{c}", use_container_width=True):
                selected_slot = st.session_state.hotbar[st.session_state.selected_slot]

                # 빈 밭이면 씨앗 심기
                if tile["crop"] is None:
                    if selected_slot["item_type"] == "seed" and selected_slot["count"] > 0:
                        tile["crop"] = selected_slot["name"]
                        tile["age"] = 0
                        tile["watered"] = False

                        remove_one_from_slot(st.session_state.selected_slot)

                        st.success(f"{tile['crop']} 씨앗을 심었습니다.")
                        st.rerun()
                    else:
                        st.warning("씨앗을 선택해야 심을 수 있습니다.")

                # 다 자랐으면 수확
                elif is_fully_grown(tile):
                    crop_name = tile["crop"]
                    crop_data = CROPS[crop_name]

                    amount = random.randint(
                        crop_data["harvest_min"],
                        crop_data["harvest_max"]
                    )

                    success_count = 0
                    failed_count = 0

                    for _ in range(amount):
                        grade = choose_grade()
                        item = make_item("crop", crop_name, 1, grade)

                        if add_to_inventory(item):
                            success_count += 1
                        else:
                            failed_count += 1

                    if success_count > 0:
                        tile["crop"] = None
                        tile["age"] = 0
                        tile["watered"] = False

                        if failed_count == 0:
                            st.success(f"{crop_name} {success_count}개를 수확했습니다.")
                        else:
                            st.warning(
                                f"{crop_name} {success_count}개만 수확했습니다. "
                                f"인벤토리가 부족해서 {failed_count}개는 못 얻었습니다."
                            )

                        st.rerun()
                    else:
                        st.error("인벤토리가 가득 찼습니다.")

                # 아직 안 자랐으면 안내
                else:
                    st.info("아직 다 자라지 않았습니다.")


st.divider()


# -----------------------------
# 밭 관리 버튼
# -----------------------------
st.subheader("💧 밭 관리")

col_water, col_next_day, col_reset = st.columns(3)

with col_water:
    if st.button("전체 물 주기 💧", use_container_width=True):
        watered_count = 0

        for row in st.session_state.field:
            for tile in row:
                if tile["crop"] is not None and not tile["watered"]:
                    tile["watered"] = True
                    watered_count += 1

        if watered_count > 0:
            st.success(f"{watered_count}개의 작물에 물을 줬습니다.")
        else:
            st.info("물을 줄 작물이 없습니다.")

        st.rerun()

with col_next_day:
    if st.button("다음 날 🌙", use_container_width=True):
        for row in st.session_state.field:
            for tile in row:
                if tile["crop"] is not None:
                    if tile["watered"]:
                        tile["age"] += 1

                        grow_days = CROPS[tile["crop"]]["grow_days"]
                        if tile["age"] > grow_days:
                            tile["age"] = grow_days

                    tile["watered"] = False

        st.session_state.day += 1
        st.rerun()

with col_reset:
    if st.button("게임 초기화 🔄", use_container_width=True):
        reset_game()
        st.rerun()


st.divider()


# -----------------------------
# 상점
# -----------------------------
st.subheader("🏪 씨앗 상점")

shop_cols = st.columns(4)

crop_names = list(CROPS.keys())

for i, crop_name in enumerate(crop_names):
    crop = CROPS[crop_name]

    with shop_cols[i]:
        st.write(f"### {crop['emoji']} {crop_name}")
        st.write(f"씨앗 가격: **{crop['seed_price']}원**")
        st.write(f"판매 기본가: **{crop['sell_price']}원**")
        st.write(f"성장 기간: **{crop['grow_days']}일**")

        if st.button(f"{crop_name} 씨앗 구매", key=f"buy_{crop_name}", use_container_width=True):
            if st.session_state.money >= crop["seed_price"]:
                item = make_item("seed", crop_name, 1)

                if add_to_inventory(item):
                    st.session_state.money -= crop["seed_price"]
                    st.success(f"{crop_name} 씨앗을 구매했습니다.")
                    st.rerun()
                else:
                    st.error("핫바가 가득 차서 구매할 수 없습니다.")
            else:
                st.warning("돈이 부족합니다.")


st.divider()


# -----------------------------
# 판매
# -----------------------------
st.subheader("💰 작물 판매")

sell_cols = st.columns(2)

with sell_cols[0]:
    if st.button("선택한 슬롯 판매", use_container_width=True):
        slot = st.session_state.hotbar[st.session_state.selected_slot]

        if slot["item_type"] == "crop" and slot["count"] > 0:
            crop_name = slot["name"]
            grade = slot["grade"]
            count = slot["count"]

            base_price = CROPS[crop_name]["sell_price"]
            multiplier = GRADE_DATA[grade]["multiplier"]

            total_price = int(base_price * multiplier * count)

            st.session_state.money += total_price
            st.session_state.hotbar[st.session_state.selected_slot] = empty_slot()

            st.success(f"{crop_name} {grade} {count}개를 {total_price}원에 판매했습니다.")
            st.rerun()
        else:
            st.warning("작물 슬롯을 선택해야 판매할 수 있습니다.")

with sell_cols[1]:
    if st.button("모든 작물 판매", use_container_width=True):
        total_price = 0
        sold_items = []

        for i, slot in enumerate(st.session_state.hotbar):
            if slot["item_type"] == "crop" and slot["count"] > 0:
                crop_name = slot["name"]
                grade = slot["grade"]
                count = slot["count"]

                base_price = CROPS[crop_name]["sell_price"]
                multiplier = GRADE_DATA[grade]["multiplier"]

                price = int(base_price * multiplier * count)
                total_price += price

                sold_items.append(f"{crop_name} {grade} x{count}")
                st.session_state.hotbar[i] = empty_slot()

        if total_price > 0:
            st.session_state.money += total_price
            st.success(f"모든 작물을 판매해서 {total_price}원을 벌었습니다.")
            st.rerun()
        else:
            st.warning("판매할 작물이 없습니다.")


st.divider()


# -----------------------------
# 가격표
# -----------------------------
st.subheader("📜 가격표")

st.write("등급 확률: 일반 70%, 은별 20%, 금별 10%")
st.write("판매 배율: 일반 100%, 은별 150%, 금별 200%")

price_table = []

for crop_name, crop in CROPS.items():
    price_table.append({
        "작물": crop_name,
        "씨앗 가격": f"{crop['seed_price']}원",
        "일반 판매가": f"{crop['sell_price']}원",
        "은별 판매가": f"{int(crop['sell_price'] * 1.5)}원",
        "금별 판매가": f"{int(crop['sell_price'] * 2)}원",
        "성장 기간": f"{crop['grow_days']}일",
        "수확량": f"{crop['harvest_min']}~{crop['harvest_max']}개"
    })

st.table(price_table)
