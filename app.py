import random
import streamlit as st
import json
import time
from pathlib import Path
from datetime import datetime

st.markdown("""
<style>
header {visibility: hiddden;}
.block-container {
    padding-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.tree-state { margin-bottom: 6px; }
.tree-state.selected { background: #fff3cd; border-radius: 6px; padding: 4px; }

.tree-state-title { font-weight: bold; margin-bottom: 2px; }

.tree-genre { margin-left: 12px; font-size: 0.9rem; }
.tree-genre.selected { color: #d6336c; font-weight: bold; }

.state-selected {
  background: #fff3cd;
  border-radius: 8px;
  padding: 6px;
}

.genre-selected {
  font-weight: bold;
}

/* ライト */
.genre-selected {
    color: #e60033;
}

/* ダーク */
html[data-theme="dark"] .genre-selected {
    color: #ff6b81;
}

/* 共通（枠だけ） */
.state-block {
    border-radius: 12px;
    padding: 12px;
}

/* 選択中だけ背景つける（ライト） */
.state-selected {
    background-color: #fff4cc;
}

/* ダークモード */
html[data-theme="dark"] .state-selected {
    background-color: #3a3320;
}

@media (prefers-color-scheme: dark) {
  .state-selected {
    background-color: #3a3320;
  }

  .genre-selected {
    color: #ff6b81;
  }
}

.state-title {
    font-weight: bold;
    margin-bottom: 2px;
}

.genre-line {
    margin-left: 12px;
    margin-bottom: 2px;
    font-size: 0.9rem;
    line-height: 1.4;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

margin-bottom: 2px;

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
    cursor: default;
    font-weight: bold;
}

html[data-theme="dark"] .bottom-drawer {
    background: #1e1e1e;
    border-top: 1px solid #444;
}

html[data-theme="dark"] .drawer-header {
    background: #2a2a2a;
    color: #f1f1f1;
}

@media (prefers-color-scheme: dark) {

  .bottom-drawer {
      background: #1e1e1e;
      border-top: 1px solid #444;
  }

  .drawer-header {
      background: #2a2a2a;
      color: #f1f1f1;
  }

}
            
.drawer-content {
    padding: 8px 12px 20px 12px;
}

.main > div {
    padding-bottom: 180px;
}
</style>
""", unsafe_allow_html=True)

DATA_FILE = Path("options_map.json")

if "selected_state" not in st.session_state:
    st.session_state.selected_state = "元気"

if "selected_genre" not in st.session_state:
    st.session_state.selected_genre = None

if "message" not in st.session_state:
    st.session_state.message = None

if "message_type" not in st.session_state:
    st.session_state.message_type = None

if "history" not in st.session_state:
    st.session_state.history = []

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

def build_tree_html(options_map, selected_state=None, selected_genre=None, use_genre_filter=False):
    html = ""

    for state, genres in options_map.items():

        is_state_selected = (state == selected_state)
        state_class = "state-selected" if is_state_selected else ""

        html += f'<div class="state-block {state_class}">'
        html += f'<div class="state-title">{state}</div>'

        for genre, options in genres.items():

            if not is_state_selected:
                is_genre_selected = False

            elif not use_genre_filter:
                # 状態だけ指定 → 全ジャンル強調
                is_genre_selected = True

            else:
                # 状態＋ジャンル指定 → 選択ジャンルだけ強調
                is_genre_selected = (genre == selected_genre)

            genre_class = "genre-selected" if is_genre_selected else ""

            html += f'<div class="genre-line {genre_class}">'
            html += f'└ {genre}：{" / ".join(options)}'
            html += '</div>'

        html += "</div>"

    return html

def kouho_list():

    tree_html = build_tree_html(
        st.session_state.options_map,
        selected_state=st.session_state.get("selected_state"),
        selected_genre=st.session_state.get("selected_genre"),
        use_genre_filter=use_genre_filter
    )

    st.markdown(f"""
    <div class="bottom-drawer">
        <div class="drawer-header">📂 候補一覧を表示</div>
        <div class="drawer-content"">
        {tree_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


if "options_map" not in st.session_state:
    st.session_state.options_map = load_options()

options_map = st.session_state.options_map

json_str = json.dumps(
    st.session_state.options_map,
    ensure_ascii=False,
    indent=2
)

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

colc, cold = st.columns(2)

with colc:

    state = st.radio(
        "今の状態は？",
        ["元気", "普通", "疲れ"],
        horizontal=True
    )
    use_genre_filter = st.checkbox("ジャンルを指定する")
with cold:
    genres = list(options_map[state].keys())
    genre = st.selectbox("ジャンル選択",genres,key="genre_select_main")
    if not use_genre_filter:
        st.caption("※ジャンルは無視され、全候補から選ばれます")
    if use_genre_filter:
        st.caption("選択した状態・ジャンルの中の候補から選ばれます")

st.session_state.selected_state = state
st.session_state.selected_genre = genre

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 ルーレット",
    "🕘 履歴",
    "📂 ジャンル編集",
    "📝 候補編集",
    "⚙ 設定"
])

with tab1:
    if st.button("回す！"):
        if use_genre_filter:
            choices = [x for x in options_map[state][genre] if x.strip()]
        else:
            candidates = []
            for g in options_map[state].values():
                candidates.extend(g)
            choices = candidates
        if choices:
            result = random.choice(choices)
            # with st.spinner("ルーレット回転中..."):
            #     time.sleep(1.5)

            st.success(f"✅ ルーレット結果：**{result}**")

            st.session_state.history.insert(0, {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "state": state,
                "genre": genre if use_genre_filter else "未指定",
                "result": result
            })
        else:
            st.warning("⚠ 候補が空だよ")
    kouho_list()

with tab2:
    st.markdown("### 🕘 ルーレット履歴")

    if not st.session_state.history:
        st.caption("まだ履歴はありません")
    else:
        for h in st.session_state.history[:50]:  # 表示は50件くらいで十分
            st.markdown(
                f"- `{h['time']}`｜{h['state']} / {h['genre']} → **{h['result']}**"
            )

    if st.button("履歴をクリア"):
        st.session_state.history = []
        st.rerun()

with tab3:
    col2, col3 = st.columns(2)
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
    kouho_list()

with tab4:
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
        delete_target = st.selectbox(
            "削除対象",
            st.session_state.options_map[state][genre]
        )
        if st.button("削除"):
            st.session_state.options_map[state][genre].remove(delete_target)
            save_options(st.session_state.options_map)
            st.rerun()
    kouho_list()

with tab5:
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

