import streamlit as st
import yt_dlp
import re 
import time 
import os
import subprocess 
from yt_dlp.utils import download_range_func
import sys
# --- PAGE SETUP ---
st.set_page_config(page_title="Pro YT Downloader", page_icon="🎬", layout="centered")

# --- APP MEMORY (SESSION STATE) ---
if 'video_fetched' not in st.session_state:
    st.session_state.video_fetched = False
if 'resolutions' not in st.session_state:
    st.session_state.resolutions = []
if 'video_title' not in st.session_state:
    st.session_state.video_title = ""

# --- TIME CONVERTER FUNCTION ---
def time_to_seconds(time_str):
    try:
        parts = time_str.split(':')
        return sum(int(x) * 60 ** i for i, x in enumerate(reversed(parts)))
    except:
        return 0

# --- CUSTOM CSS & ANIMATIONS ---
custom_css = """
<style>
    .stApp { background: linear-gradient(-45deg, #1A1A2E, #16213E, #0F3460, #E94560); background-size: 400% 400%; animation: gradientBG 15s ease infinite; }
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    
    .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); border-radius: 20px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); text-align: center; margin-bottom: 30px; transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); cursor: default; }
    .glass-card:hover { transform: translateY(-10px) scale(1.02); box-shadow: 0 15px 45px 0 rgba(233, 69, 96, 0.4); border: 1px solid rgba(233, 69, 96, 0.5); }
    
    .glow-title { font-family: 'Helvetica', sans-serif; font-size: 3.5em; font-weight: 900; color: #ffffff; text-transform: uppercase; animation: neonGlow 2s ease-in-out infinite alternate; }
    @keyframes neonGlow { from { text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #E94560, 0 0 40px #E94560; } to { text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #0F3460, 0 0 20px #0F3460; } }
    
    div[data-baseweb="input"], div[data-baseweb="select"] > div { background-color: rgba(255,255,255,0.1) !important; border-radius: 10px; border: 1px solid transparent !important; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; color: white !important;}
    div[data-baseweb="input"] input { color: white !important; }
    div[data-baseweb="input"]:hover, div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:hover { transform: translateY(-5px) !important; box-shadow: 0px 10px 20px rgba(233, 69, 96, 0.2) !important; border: 1px solid #E94560 !important; background-color: rgba(255,255,255,0.15) !important; }
    
    div.stButton > button { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; border-radius: 50px !important; border: 2px solid #E94560 !important; background-color: transparent !important; color: white !important; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; }
    div.stButton > button:hover { transform: translateY(-8px) scale(1.02) !important; background-color: #E94560 !important; box-shadow: 0px 15px 25px rgba(233, 69, 96, 0.4) !important; color: white !important; }
    
    div[role="radiogroup"] > label { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; padding: 10px 20px !important; border-radius: 15px !important; background-color: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; cursor: pointer !important; }
    div[role="radiogroup"] > label:hover { transform: translateY(-6px) !important; background-color: rgba(233, 69, 96, 0.15) !important; border: 1px solid #E94560 !important; box-shadow: 0px 10px 20px rgba(233, 69, 96, 0.3) !important; }
    
    .neon-text { color: #00FFCC !important; font-family: 'Helvetica', sans-serif !important; font-weight: 800 !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; font-size: 13px !important; text-shadow: 0px 0px 8px rgba(0, 255, 204, 0.4) !important; margin-bottom: 5px !important; }
    
    div[data-testid="stCheckbox"] { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; padding: 10px 15px !important; border-radius: 12px !important; background-color: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; cursor: pointer !important; }
    div[data-testid="stCheckbox"]:hover { transform: translateY(-6px) !important; background-color: rgba(233, 69, 96, 0.15) !important; border: 1px solid #E94560 !important; box-shadow: 0px 10px 20px rgba(233, 69, 96, 0.3) !important; }
    
    .stats-box { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 10px; font-family: 'Courier New', monospace; color: #00FFCC; text-align: center; margin-top: 10px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- UI STRUCTURE ---
st.markdown("""
<div class="glass-card">
    <div class="glow-title">YT PRO</div>
    <p style="color: #A0AEC0; font-size: 18px; letter-spacing: 2px;">ULTIMATE DOWNLOADER</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='neon-text'>🔗 Paste YouTube Video OR Playlist URL:</div>", unsafe_allow_html=True)
url = st.text_input("URL", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")

# --- STEP 1: FETCH QUALITIES ---
if st.button("🔍 FETCH QUALITIES", use_container_width=True):
    if not url:
        st.error("⚠️ Please enter a URL first!")
    else:
        with st.status("Scanning YouTube for available qualities... ⏳", expanded=True) as status:
            try:
                ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': 'in_playlist'}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    st.session_state.video_title = info_dict.get('title', 'Unknown Title/Playlist')
                    
                    resolutions = set()
                    entries = info_dict.get('entries')
                    formats = info_dict.get('formats', [])
                    if entries and not formats:
                        formats = entries[0].get('formats', []) if entries[0] else []
                        
                    for f in formats:
                        if f.get('vcodec') != 'none' and f.get('height'):
                            resolutions.add(f.get('height'))
                    
                    st.session_state.resolutions = sorted(list(resolutions), reverse=True)
                    if not st.session_state.resolutions:
                        st.session_state.resolutions = ["Best"]
                        
                    st.session_state.video_fetched = True
                status.update(label="Scanned Successfully! ✅", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Scan Failed! ❌", state="error", expanded=False)
                st.error(f"Error: {e}")

# --- STEP 2: SHOW OPTIONS & DOWNLOAD ---
if st.session_state.video_fetched:
    st.write("---")
    st.markdown(f"<div class='neon-text'>🎥 Selected: <span style='color: white; text-shadow: none;'>{st.session_state.video_title}</span></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='neon-text'>⚙️ Select Quality:</div>", unsafe_allow_html=True)
        res_options = [f"{r}p" for r in st.session_state.resolutions] if st.session_state.resolutions != ["Best"] else ["Best"]
        selected_res_str = st.selectbox("Quality", res_options, label_visibility="collapsed")
        
    with col2:
        st.markdown("<div class='neon-text'>🎬 Format:</div>", unsafe_allow_html=True)
        format_choice = st.radio("Format", ["Video (MP4)", "Audio (MP3)"], horizontal=True, label_visibility="collapsed")

    # --- ADVANCED OPTIONS & AI ---
    st.write("")
    st.markdown("<div class='neon-text'>🚀 Pro & AI Features:</div>", unsafe_allow_html=True)
    
    opt_col1, opt_col2, opt_col3 = st.columns(3)
    with opt_col1:
        is_playlist = st.toggle("📚 Download Playlist")
    with opt_col2:
        clip_toggle = st.toggle("✂️ Trimming (Clip)")
    with opt_col3:
        # NAYA AI TOGGLE
        karaoke_toggle = st.toggle("🎤 AI Karaoke Split", disabled=(format_choice != "Audio (MP3)"), help="Extracts Vocals & Beats. Works only on Audio (MP3).")
    
    start_time, end_time = "", ""
    if clip_toggle:
        if is_playlist:
            st.warning("⚠️ Trimming is not recommended for Playlists.")
        clip_col1, clip_col2 = st.columns(2)
        with clip_col1:
            start_time = st.text_input("Start Time (MM:SS)", value="00:00")
        with clip_col2:
            end_time = st.text_input("End Time (MM:SS)", value="01:30")

    st.write("")

    if st.button("🚀 START DOWNLOAD", use_container_width=True):
        
        if clip_toggle:
            start_sec = time_to_seconds(start_time)
            end_sec = time_to_seconds(end_time)
            if end_sec <= start_sec:
                st.error("⚠️ End time Start time se bara hona chahiye!")
                st.stop()

        progress_bar = st.progress(0.0)
        stats_text = st.empty()
        last_update = [0.0] 

        def my_hook(d):
            if d['status'] == 'downloading':
                try:
                    current_time = time.time()
                    if current_time - last_update[0] > 0.5:
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        downloaded = d.get('downloaded_bytes', 0)
                        
                        percent = downloaded / total if total > 0 else 0.0 
                        percent = max(0.0, min(1.0, float(percent)))
                        progress_bar.progress(percent)
                        
                        raw_speed = str(d.get('_speed_str', 'N/A'))
                        raw_eta = str(d.get('_eta_str', 'N/A'))
                        raw_percent = str(d.get('_percent_str', f"{int(percent*100)}%"))
                        
                        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                        speed = ansi_escape.sub('', raw_speed).strip()
                        eta = ansi_escape.sub('', raw_eta).strip()
                        percent_str = ansi_escape.sub('', raw_percent).strip()
                        
                        stats_text.markdown(f"<div class='stats-box'>🚀 Speed: {speed} &nbsp;|&nbsp; ⏳ ETA: {eta} &nbsp;|&nbsp; 📊 Done: {percent_str}</div>", unsafe_allow_html=True)
                        last_update[0] = current_time 
                except Exception:
                    pass
            elif d['status'] == 'finished':
                progress_bar.progress(1.0)
                stats_text.markdown("<div class='stats-box' style='color: yellow;'>✅ Download 100%! Processing... ⏳</div>", unsafe_allow_html=True)

        clip_msg = f" (Clipping from {start_time} to {end_time})" if clip_toggle and not is_playlist else ""
        playlist_msg = " [PLAYLIST MODE]" if is_playlist else ""

        with st.status(f"Downloading in {selected_res_str}{playlist_msg}{clip_msg}... Please wait! ⏳", expanded=True) as status:
            try:
                if is_playlist:
                    output_template = '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'
                else:
                    output_template = '%(title)s.%(ext)s'

                selected_height = selected_res_str.replace("p", "") if selected_res_str != "Best" else "1080"
                
                if format_choice == "Audio (MP3)":
                    selected_format = 'bestaudio/best'
                    my_postprocessors = [
                        {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                        {'key': 'FFmpegMetadata', 'add_metadata': True},
                        {'key': 'EmbedThumbnail', 'already_have_thumbnail': False},
                    ]
                    write_thumb = True 
                else:
                    if selected_res_str == "Best":
                        selected_format = 'best'
                    else:
                        selected_format = f'bestvideo[height<={selected_height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                    my_postprocessors = [{'key': 'FFmpegMetadata', 'add_metadata': True}]
                    write_thumb = False 

                ydl_opts = {
                    'outtmpl': output_template, 
                    'noplaylist': not is_playlist, 
                    'format': selected_format,
                    'quiet': True,
                    'no_warnings': True,
                    'socket_timeout': 60,
                    'retries': 15,
                    'fragment_retries': 15,
                    'progress_hooks': [my_hook],
                    'writethumbnail': write_thumb, 
                    'postprocessors': my_postprocessors 
                }

                # 1. DOWNLOAD STEP
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    raw_filename = ydl.prepare_filename(info_dict)
                
                base, ext = os.path.splitext(raw_filename)
                actual_ext = ".mp3" if format_choice == "Audio (MP3)" else ".mp4"
                final_filename = base + actual_ext
                
                # 2. LOCAL TRIMMING (Agar ON hai)
                if clip_toggle and not is_playlist:
                    stats_text.markdown("<div class='stats-box' style='color: #00FFCC;'>✂️ Applying Local Fast-Trim... ⏳</div>", unsafe_allow_html=True)
                    trimmed_filename = base + "_trimmed" + actual_ext
                    cmd = ['ffmpeg', '-y', '-i', final_filename, '-ss', start_time, '-to', end_time, '-c', 'copy', trimmed_filename]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if os.path.exists(trimmed_filename):
                        os.remove(final_filename)
                        os.rename(trimmed_filename, final_filename)
                        
                # 3. AI KARAOKE SPLITTER (Agar ON hai aur MP3 hai)
                ai_msg = ""
                if karaoke_toggle and format_choice == "Audio (MP3)":
                    stats_text.markdown("<div class='stats-box' style='color: #FF00FF;'>🤖 AI Splitting Vocals... (Check VS Code Terminal!) ⏳</div>", unsafe_allow_html=True)
                    
                    # Naya Safe Command (using sys.executable taake .venv sahi se chale)
                    spleeter_cmd = [
                        sys.executable, '-m', 'spleeter', 'separate', 
                        '-p', 'spleeter:2stems', 
                        '-o', 'AI_Karaoke_Tracks', 
                        final_filename
                    ]
                    
                    # DEVNULL hata diya! Ab VS Code ke terminal mein processing nazar aayegi
                    subprocess.run(spleeter_cmd)
                    ai_msg = " + 🎤 AI Karaoke Splitted (Check 'AI_Karaoke_Tracks' Folder!)"

                status.update(label="All Tasks Completed! 🎉", state="complete", expanded=False)
                st.balloons() 
                st.success(f"Successfully downloaded {selected_res_str} {format_choice}{playlist_msg}{clip_msg}{ai_msg}!")
                stats_text.markdown("<div class='stats-box' style='color: #00FFCC;'>🎉 Job Done! Check your local folder.</div>", unsafe_allow_html=True)
                
            except Exception as e:
                status.update(label="Download Failed! ❌", state="error", expanded=False)
                st.error(f"Error details: {e}")