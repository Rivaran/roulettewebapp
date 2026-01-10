import random
import streamlit as st
import json
from pathlib import Path

st.markdown("""
<style>
.bottom-drawer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #f8f9fa;
    border-top: 1px solid #ccc;
    z-index: 1000;
    max-height: 60vh;
    overflow-y: auto;
    transition: transform 0.3s ease;
}

.drawer-header {
    padding: 8px 12px;
    background: #e9ecef;
    cursor: pointer;
    font-weight: bold;
}

.drawer-content {
    padding: 8px 12px 20px 12px;
}

.main > div {
    padding-bottom: 300px;
}
</style>
""", unsafe_allow_html=True)

DATA_FILE = Path("options_map.json")

if "message" not in st.session_state:
    st.session_state.message = None
if "message_type" not in st.session_state:
    st.session_state.message_type = None

def is_valid_options_map(data):
    if not isinstance(data, dict):
        return False
    for state, genres in data.items():
        if not isinstance(genres, dict):
            return False
        for genre, items in genres.items():
            if not isinstance(items, list):
                return False
    return True

def load_from_uploaded_json():
    uploaded_file = st.session_state.get("uploaded_json")
    if uploaded_file is None:
        return
    try:
        loaded_data = json.load(uploaded_file)
        if is_valid_options_map(loaded_data):
            st.session_state.options_map = loaded_data
            st.session_state.message = "設定を読み込みました"
            st.session_state.message_type = "success"
        else:
            st.session_state.message = "対応していないフォーマットです"
            st.session_state.message_type = "error"

        for key in ["delete_genre", "new_genre"]:
            st.session_state.pop(key, None)

    except Exception:
        st.session_state.message = "JSONの読み込みに失敗しました"
        st.session_state.message_type = "error"

def load_options():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "元気": {
            "運動": ["ランニング", "筋トレ"],
            "掃除": ["玄関掃除", "風呂掃除"],
        },
        "普通": {
            "家事": ["洗濯", "皿洗い"],
            "勉強": ["英語", "プログラミング"],
        },
        "疲れ": {
            "休憩": ["ストレッチ", "昼寝"],
            "娯楽": ["ゲーム", "動画"],
        },
    }

def save_options(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def build_tree_html(options_map):
    html = ""
    for mood, genres in options_map.items():
        html += f"<b>{mood}</b><br>"
        for g, items in genres.items():
            if items:
                html += f"&nbsp;&nbsp;└ {g}：{' / '.join(items)}<br>"
            else:
                html += f"&nbsp;&nbsp;└ {g}：（なし）<br>"
        html += "<br>"
    return html

if "options_map" not in st.session_state:
    st.session_state.options_map = load_options()

options_map = st.session_state.options_map

json_str = json.dumps(
    st.session_state.options_map,
    ensure_ascii=False,
    indent=2
)

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 ルーレット",
    "📂 ジャンル編集",
    "📝 候補編集",
    "⚙ 設定"
])

with tab1:
    st.set_page_config(page_title="気分ルーレット", page_icon="🎯")
    st.markdown(
        """
        <h1 style="
            white-space: nowrap;
            text-align: left;
            font-size: 2rem;
        ">
        🎯 気分ルーレット
        </h1>
        """,
        unsafe_allow_html=True
    )

    colx, coly = st.columns(2)

    with colx:
        state = st.radio(
            "今の状態は？",
            ["元気", "普通", "疲れ"],
            horizontal=True
        )
        genres = list(options_map[state].keys())
        genre = st.selectbox("ジャンル選択",genres,key="genre_select_main")
            
with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        if not genres:
            st.warning("この状態にはジャンルがありません")
            st.stop()
        st.write(f"選択中のジャンル：{genre}")
    with col2:
    # --- ジャンル追加 ---
        new_genre = st.text_input("ジャンル追加", key="new_genre")
        if st.button("ジャンルを追加"):
            if new_genre and new_genre not in st.session_state.options_map[state]:
                st.session_state.options_map[state][new_genre] = []
                save_options(st.session_state.options_map)
                st.rerun()

    with col3:
        # --- ジャンル削除 ---
        with st.expander("ジャンルを削除"):
            genre_to_delete = st.selectbox(
                "削除するジャンル",
                list(st.session_state.options_map[state].keys()),
                key="delete_genre"
            )
            if st.button("ジャンルを削除"):
                # 念のため、空でも削除可（仕様）
                st.session_state.options_map[state].pop(genre_to_delete, None)
                save_options(st.session_state.options_map)
                st.rerun()

with tab3:
    if genre not in st.session_state.options_map[state]:
        st.warning("このジャンルは削除されました。再選択してください。")
        st.stop()

    st.markdown("##### 候補")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.text("候補一覧")
        st.markdown(
            "\n".join([f"- {opt}" for opt in st.session_state.options_map[state][genre]])
        )
    with col5:
        new_option = st.text_input("候補追加")
        if st.button("追加"):
            if new_option:
                st.session_state.options_map[state][genre].append(new_option)
                save_options(st.session_state.options_map)
                st.rerun()
    with col6:
        with st.expander("候補を削除"):
            delete_target = st.selectbox(
                "削除対象",
                st.session_state.options_map[state][genre]
            )
            if st.button("削除"):
                st.session_state.options_map[state][genre].remove(delete_target)
                save_options(st.session_state.options_map)
                st.rerun()

    with coly:
        if st.button("回す！"):
            choices = [x for x in options_map[state][genre] if x.strip()]
            if choices:
                result = random.choice(choices)
                st.success(f"✅ ルーレット結果：**{result}**")
            else:
                st.warning("⚠ 候補が空だよ")

with tab4:
    cola, colb = st.columns([1, 2])

    with cola:
        st.download_button(
            label="設定をファイル(JSON)で保存",
            data=json_str,
            file_name="kibun_roulette.json",
            mime="application/json"
        )

    with colb:
        message_area = st.empty()

        if st.session_state.message:
            if st.session_state.message_type == "success":
                st.toast(st.session_state.message, icon="✅")
                st.session_state.message = None
            else:
                message_area.error(st.session_state.message)

        st.file_uploader(
            "設定ファイル(JSON)を読み込む",
            type="json",
            key="uploaded_json",
            on_change=load_from_uploaded_json
        )

tree_html = build_tree_html(st.session_state.options_map)

st.markdown(f"""
<div class="bottom-drawer">
  <details>
    <summary class="drawer-header">📂 候補一覧を表示</summary>
    <div class="drawer-content">
      {tree_html}
    </div>
  </details>
</div>
""", unsafe_allow_html=True)
