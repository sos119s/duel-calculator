import streamlit as st
import math

def prob_any(total_deck, hand_size, n):
    if n <= 0 or n > total_deck: return 0.0
    return 1.0 - (math.comb(total_deck - n, hand_size) / math.comb(total_deck, hand_size))

def prob_combo(total_deck, hand_size, card_counts):
    # コンボ成立確率（各カードを1枚以上引く確率の積）
    p = 1.0
    for count in card_counts:
        p *= prob_any(total_deck, hand_size, count)
    return p

def main():
    st.title("初動率計算")
    deck_size = st.slider("デッキ合計枚数", 40, 60, 40)
    hand_size = st.slider("初手枚数", 3, 8, 5)

    if 'deck' not in st.session_state: st.session_state.deck = {}
    if 'combos' not in st.session_state: st.session_state.combos = []

    # 1. カード登録
    with st.form(key="add_card", clear_on_submit=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        name = c1.text_input("カード名")
        count = c2.number_input("枚数", 1, 4, 3)
        if c3.form_submit_button("追加"): st.session_state.deck[name] = count

    # 2. 1枚初動計算
    st.write("---")
    st.subheader("1枚初動")
    starters = []
    for card in list(st.session_state.deck.keys()):
        cols = st.columns([3, 1, 1, 1])
        cols[0].text(card)
        st.session_state.deck[card] = cols[1].number_input("枚", 1, 4, st.session_state.deck[card], key=f"n_{card}", label_visibility="collapsed")
        if cols[2].checkbox("初動", key=f"s_{card}"): starters.append(st.session_state.deck[card])
        if cols[3].button("削除", key=f"d_{card}"): del st.session_state.deck[card]; st.rerun()

    s_sum = sum(starters)
    p_s = prob_any(deck_size, hand_size, s_sum)
    st.metric("1枚初動率", f"{p_s*100:.2f}%")

    # 3. コンボ計算＆合計
    st.write("---")
    st.subheader("コンボ初動")
    selected = st.multiselect("カードを選んでコンボ追加", list(st.session_state.deck.keys()))
    if st.button("コンボに追加"): st.session_state.combos.append(selected)

    combo_probs = []
    for i, combo in enumerate(st.session_state.combos):
        counts = [st.session_state.deck[c] for c in combo]
        p = prob_combo(deck_size, hand_size, counts)
        combo_probs.append(p)
        st.write(f"コンボ{i+1}: {' + '.join(combo)} ({p*100:.2f}%)")
        if st.button(f"コンボ{i+1}削除", key=f"del_c_{i}"):
            st.session_state.combos.pop(i); st.rerun()

    # 合計確率の計算（「いずれかのコンボが成立する」確率）
    # 簡易的に「1枚初動」＋「全コンボ」で計算（重複を考慮した厳密計算は複雑なため、ここでは近似として提示）
    if combo_probs:
        # すべてのコンボが失敗する確率を計算して1から引く手法
        fail_p = (1 - p_s)
        for p in combo_probs:
            fail_p *= (1 - p)
        total_p = 1 - fail_p
        st.metric("合計初動率", f"{total_p*100:.2f}%")

    if st.button("全リセット"):
        st.session_state.deck = {}; st.session_state.combos = []; st.rerun()

if __name__ == "__main__":
    main()
