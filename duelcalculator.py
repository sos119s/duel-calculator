import streamlit as st
import math

# 超幾何分布を用いた「1枚以上引く確率」
def prob_any(total_deck, hand_size, n):
    if n <= 0 or n > total_deck: return 0.0
    return 1.0 - (math.comb(total_deck - n, hand_size) / math.comb(total_deck, hand_size))

def main():
    st.title("初動率計算")

    deck_size = st.slider("デッキ合計枚数", 40, 60, 40)
    hand_size = st.slider("初手枚数", 3, 7, 5)

    if 'deck' not in st.session_state: st.session_state.deck = {}

    # フォームを使用して入力の競合を防ぎ、リセットを自動化する
    with st.form(key="add_card_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        name = col1.text_input("カード名")
        count = col2.number_input("枚数", 1, 4, 3)
        submit_button = col3.form_submit_button("追加")
        
        if submit_button and name:
            st.session_state.deck[name] = count

    st.write("---")
    
    # リスト表示・チェック
    h = st.columns([2, 1, 1, 1, 1, 1])
    h[0].write("**カード名**"); h[1].write("**枚**"); h[2].write("**初**"); h[3].write("**A**"); h[4].write("**B**"); h[5].write("**C**")

    starters, g_a, g_b, g_c = [], [], [], []
    
    # リストのコピーを作成してループ
    for card in list(st.session_state.deck.keys()):
        cols = st.columns([2, 1, 1, 1, 1, 1, 1])
        cols[0].text(card)
        st.session_state.deck[card] = cols[1].number_input("枚", 1, 4, st.session_state.deck[card], key=f"n_{card}", label_visibility="collapsed")
        
        if cols[2].checkbox("初", key=f"s_{card}"): starters.append(st.session_state.deck[card])
        if cols[3].checkbox("A", key=f"a_{card}"): g_a.append(st.session_state.deck[card])
        if cols[4].checkbox("B", key=f"b_{card}"): g_b.append(st.session_state.deck[card])
        if cols[5].checkbox("C", key=f"c_{card}"): g_c.append(st.session_state.deck[card])
        
        if cols[6].button("削", key=f"d_{card}"): 
            del st.session_state.deck[card]
            st.rerun()

    st.write("---")
    
    # 各グループを引く確率
    s_sum, a_sum, b_sum, c_sum = sum(starters), sum(g_a), sum(g_b), sum(g_c)
    p_s = prob_any(deck_size, hand_size, s_sum)
    p_a = prob_any(deck_size, hand_size, a_sum)
    p_b = prob_any(deck_size, hand_size, b_sum)
    p_c = prob_any(deck_size, hand_size, c_sum)

    # 複合コンボ確率
    p_ab = p_a * p_b
    p_abc = p_a * p_b * p_c

    # 包含排除による「いずれか成立する確率」の厳密計算
    p_union = p_s + p_ab + p_abc - (p_s*p_ab + p_s*p_abc + p_ab*p_abc) + (p_s*p_ab*p_abc)

    # 結果表示
    st.subheader("確率")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("1枚初動", f"{p_s*100:.2f}%")
    r2.metric("AB初動", f"{p_ab*100:.2f}%")
    r3.metric("ABC初動", f"{p_abc*100:.2f}%")
    r4.metric("合計", f"{max(0, p_union)*100:.2f}%")

    st.info(f"内訳: 初動:{s_sum} / A:{a_sum} / B:{b_sum} / C:{c_sum}")

    if st.button("全リセット"):
        st.session_state.deck = {}; st.rerun()

if __name__ == "__main__":
    main()