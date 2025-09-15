"""
Layout components for the PRD Generator Streamlit application.
This module contains all UI layout functions, CSS styles, and component builders.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
import uuid


def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="AI PRD Generator - Interactive Chat",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def load_custom_css():
    """Load custom CSS styles for the application"""
    st.markdown("""
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .chat-window {
        /* max-height is set inline to respect viewport; keeping overflow here */
        overflow-y: auto;
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.75rem;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #1f77b4;
    }
    .assistant-message {
        background-color: #e8f4fd;
        border-left-color: #17a2b8;
    }
    .fixed-col {
        position: sticky;
        top: 1rem;
        max-height: calc(100vh - 2rem);
        overflow-y: auto;
    }
    .prd-preview {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
    }
    .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(248, 249, 250, 0.95);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-radius: 0.5rem;
        z-index: 1000;
        min-height: 400px;
    }
    .loading-content {
        text-align: center;
        padding: 20px;
    }
    .spinner {
        border: 6px solid #e3f2fd;
        border-top: 6px solid #2196f3;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }
    .loading-text {
        font-size: 18px;
        font-weight: 600;
        color: #2196f3;
        margin-bottom: 10px;
    }
    .loading-subtext {
        font-size: 14px;
        color: #6c757d;
        max-width: 300px;
        line-height: 1.4;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    .loading-text {
        animation: pulse 2s ease-in-out infinite;
    }
    .version-nav {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 0.75rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .diff-view {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #fafafa;
        min-height: 500px;
        max-height: 80vh;
        overflow-y: auto;
        font-size: 14px;
        line-height: 1.6;
    }
    .diff-view table {
        width: 100% !important;
        table-layout: fixed;
    }
    .diff-view td {
        vertical-align: top !important;
        padding: 8px 12px !important;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    .session-item {
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 0.375rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .session-item:hover {
        background-color: #e9ecef;
        border-color: #007bff;
    }
    .session-item.active {
        background-color: #d1ecf1;
        border-color: #bee5eb;
    }
    .user-prompt-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #495057;
    }
    .prompt-header {
        background-color: #e9ecef;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
        color: #6c757d;
    }
    </style>
    """, unsafe_allow_html=True)


def display_chat_message(role: str, content: str):
    """Display a formatted chat message"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>Assistant:</strong> {content}
        </div>
        """, unsafe_allow_html=True)


def render_sidebar_sessions(db, all_sessions: List[Dict], create_new_session_callback, load_session_callback):
    """Render the session management section in sidebar"""
    st.header("🔧 Sessions")
    
    if st.button("🆕 New Session", use_container_width=True):
        create_new_session_callback()
        st.rerun()
    
    st.divider()
    
    # Session list
    if all_sessions:
        st.subheader("📁 All Sessions")
        for session in all_sessions:
            is_current = session['session_id'] == st.session_state.session_id
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if st.button(
                        f"📝 {session['product_name']}", 
                        key=f"session_{session['session_id']}",
                        use_container_width=True,
                        type="primary" if is_current else "secondary"
                    ):
                        if not is_current:
                            load_session_callback(session['session_id'], session['product_name'])
                            st.rerun()
                
                with col2:
                    st.caption(f"v{session['version_count']}")
                
                if is_current:
                    st.caption("🟢 Active")
                else:
                    st.caption(f"Updated: {session['updated_at'][:10]}")


def render_sidebar_download(download_prd_callback):
    """Render the download PRD section in sidebar"""
    if st.session_state.current_prd and st.session_state.viewing_version == st.session_state.current_version:
        content, filename = download_prd_callback()
        if content and filename:
            st.download_button(
                label="📥 Download PRD",
                data=content,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True
            )


def render_sidebar_version_history(db, versions: List[Dict]):
    """Render the version history section in sidebar"""
    st.header("📚 Version History")
    
    if versions:
        for version in versions:
            is_current_viewing = version['version_number'] == st.session_state.viewing_version
            is_latest = version['version_number'] == st.session_state.current_version
            
            # Create clickable version item
            version_label = f"v{version['version_number']}{' (Latest)' if is_latest else ''}"
            
            # Make version clickable to directly view it
            if st.button(
                version_label, 
                key=f"goto_v{version['version_number']}", 
                use_container_width=True,
                type="primary" if is_current_viewing else "secondary"
            ):
                st.session_state.viewing_version = version['version_number']
                # Default to compare mode if not current version, otherwise preview
                st.session_state.show_diff = (version['version_number'] != st.session_state.current_version)
                st.rerun()
            
            # Show details in expander only if currently viewing this version
            if is_current_viewing:
                with st.expander("ℹ️ Version Details", expanded=False):
                    st.caption(f"Created: {version['created_at'][:10]}")
                    
                    # Show change description if available
                    if version['change_description']:
                        st.write(f"**Changes:** {version['change_description'][:80]}{'...' if len(version['change_description']) > 80 else ''}")
    else:
        st.info("No versions available yet.")


@st.dialog("⚠️ Confirm Rollback")
def rollback_confirmation_dialog(db):
    """Show rollback confirmation dialog"""
    st.markdown(f"""
    ### 🔄 Rollback to Version {st.session_state.rollback_target}
    
    **⚠️ WARNING: This action cannot be undone!**
    
    This will permanently:
    - ❌ Delete Version {st.session_state.rollback_target + 1} through {st.session_state.current_version}
    - ❌ Remove all chat messages after Version {st.session_state.rollback_target}
    - ❌ Lose all progress made after this version
    
    **Current version:** {st.session_state.current_version} → **New version:** {st.session_state.rollback_target}
    """)
    
    col_confirm, col_cancel = st.columns([1, 1])
    
    with col_confirm:
        if st.button("✅ **YES, ROLLBACK**", key="confirm_rollback", use_container_width=True, type="primary"):
            # Perform rollback
            if db.rollback_to_version(st.session_state.session_id, st.session_state.rollback_target):
                # Update session state
                st.session_state.current_version = st.session_state.rollback_target
                st.session_state.viewing_version = st.session_state.rollback_target
                st.session_state.show_diff = False
                
                # Reload messages from database
                st.session_state.messages = db.get_chat_history(st.session_state.session_id)
                
                # Get the content of the rollback version
                version_data = db.get_version_by_number(st.session_state.session_id, st.session_state.rollback_target)
                if version_data:
                    st.session_state.current_prd = version_data['content']
                
                # Set toast to show after rerun
                st.session_state.show_toast = "rollback_success"
                
                st.success(f"✅ Successfully rolled back to Version {st.session_state.rollback_target}!")
                
                # Clean up
                if hasattr(st.session_state, 'rollback_target'):
                    del st.session_state.rollback_target
                
                st.rerun()
            else:
                st.error("❌ Failed to rollback. Please try again.")
    
    with col_cancel:
        if st.button("❌ **CANCEL**", key="cancel_rollback", use_container_width=True):
            # Clean up
            if hasattr(st.session_state, 'rollback_target'):
                del st.session_state.rollback_target
            st.rerun()


def render_rollback_modal(db):
    """Render the rollback confirmation modal using st.dialog"""
    if hasattr(st.session_state, 'rollback_target') and st.session_state.rollback_target:
        rollback_confirmation_dialog(db)


def render_main_layout():
    """Render the main two-column layout with PRD preview taking 2/3 and chat 1/3"""
    return st.columns([2, 1])


def render_initial_setup_form():
    """Render the initial PRD setup form"""
    st.subheader("🚀 Start New PRD")
    
    product_name = st.text_input("Product Name", placeholder="e.g., Smart Meeting Scheduler")
    
    mrd_file = st.file_uploader("Upload MRD Document (optional)", type=["txt", "pdf", "docx"])
    
    additional_context = st.text_area(
        "Additional Context", 
        placeholder="Provide any additional context or requirements...",
        height=100
    )
    
    return product_name, mrd_file, additional_context


def render_chat_interface(messages: List[Dict], max_height: str = "calc(100vh - 200px)", auto_scroll: bool = True):
    """Render the chat message interface inside a scrollable viewport.

    Args:
        messages: List of chat messages to display.
        max_height: CSS size for the maximum height of chat area (e.g., '65vh', '500px', 'calc(100vh - 300px)').
        auto_scroll: If True, auto-scroll to the bottom after render.
    """
    chat_div_id = f"chat-window-{uuid.uuid4().hex}"
    st.markdown(f'<div id="{chat_div_id}" class="chat-window" style="max-height: {max_height};">', unsafe_allow_html=True)
    for message in messages:
        with st.container():
            role = message.get("role") or message.get("type", "assistant")
            content = message.get("content", "")
            display_chat_message(role, content)
    st.markdown('</div>', unsafe_allow_html=True)

    if auto_scroll:
        st.markdown(
            f"""
            <script>
            setTimeout(function() {{
                var el = document.getElementById('{chat_div_id}');
                if (el) {{ el.scrollTop = el.scrollHeight; }}
            }}, 0);
            </script>
            """,
            unsafe_allow_html=True,
        )


def render_quick_actions():
    """Render quick action pills for chat interface"""
    st.markdown("**Quick Actions:**")
    
    option_map = {
        "add_section": ":material/add_circle:",
        "enhance_detail": ":material/edit_note:",
        "simplify": ":material/compress:",
        "overview": ":material/summarize:",
        "auto_improve": ":material/auto_fix_high:",
    }
    
    action_labels = {
        "add_section": "Add Section",
        "enhance_detail": "Add Details", 
        "simplify": "Simplify",
        "overview": "Overview",
        "auto_improve": "Auto Improve"
    }
    
    selection = st.pills(
        "Quick Actions",
        options=list(option_map.keys()),
        format_func=lambda option: f"{option_map[option]} {action_labels[option]}",
        selection_mode="single",
        label_visibility="collapsed"
    )
    
    # Return selected action for further processing
    return selection


def render_chat_input():
    """Render the chat input area with send/clear buttons"""
    # Initialize input counter for unique keys
    if 'input_counter' not in st.session_state:
        st.session_state.input_counter = 0
    
    user_input = st.text_area(
        "What would you like to change in the PRD?", 
        placeholder="e.g., Add a section about mobile app features, Update the timeline, Remove the analytics requirements...",
        height=80,
        key=f"chat_input_{st.session_state.input_counter}"
    )
    
    col_send, col_clear = st.columns([3, 1])
    return user_input, col_send, col_clear


def render_historical_version_view():
    """Render the historical version viewing interface"""
    # Create a styled info box for historical version viewing
    st.info(f"📚 **Viewing Version {st.session_state.viewing_version}** (Historical)")
    
    # Back to current button
    if st.button("🔙 Back to Current Version", use_container_width=True):
        st.session_state.viewing_version = st.session_state.current_version
        st.session_state.show_diff = False
        st.rerun()
    
    st.markdown("---")
    st.write("**This is a historical version. To make changes, return to the current version.**")


def render_loading_overlay(message: str = "Processing your request..."):
    """Render a loading overlay"""
    st.markdown(f"""
    <div class="loading-overlay">
        <div class="loading-content">
            <div class="spinner"></div>
            <div class="loading-text">{message}</div>
            <div class="loading-subtext">This may take a few moments. Please wait...</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_prd_preview_section():
    """Render the PRD preview section header"""
    st.header("📄 PRD Preview")


def render_version_navigation(versions: List[Dict]):
    """Render version navigation controls"""
    if len(versions) > 1:
        # First row - navigation between versions
        col_nav = st.columns([1, 1, 1, 2])
        
        with col_nav[0]:
            if st.session_state.viewing_version > 1:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.viewing_version -= 1
                    st.session_state.show_diff = (st.session_state.viewing_version != st.session_state.current_version)
                    st.rerun()
        
        with col_nav[1]:
            if st.session_state.viewing_version < st.session_state.current_version:
                if st.button("➡️ Next", use_container_width=True):
                    st.session_state.viewing_version += 1
                    st.session_state.show_diff = (st.session_state.viewing_version != st.session_state.current_version)
                    st.rerun()
        
        with col_nav[2]:
            if st.session_state.viewing_version != st.session_state.current_version:
                if st.button("🔄 Current", use_container_width=True):
                    st.session_state.viewing_version = st.session_state.current_version
                    st.session_state.show_diff = False
                    st.rerun()
        
        with col_nav[3]:
            st.write(f"**Version {st.session_state.viewing_version} of {st.session_state.current_version}**")
        
        # Second row - action buttons for current version
        if st.session_state.viewing_version != st.session_state.current_version:
            st.markdown("---")
            st.markdown("**Version Actions:**")
            
            # Create pills for actions
            action_map = {
                "compare": ":material/compare_arrows:",
                "preview": ":material/visibility:", 
                "rollback": ":material/history:"
            }
            
            action_labels = {
                "compare": "Compare Mode",
                "preview": "Preview Mode",
                "rollback": "Rollback to This"
            }
            
            # Determine current mode for selection
            current_mode = "compare" if st.session_state.show_diff else "preview"
            
            selection = st.pills(
                "Version Actions",
                options=list(action_map.keys()),
                format_func=lambda option: f"{action_map[option]} {action_labels[option]}",
                selection_mode="single",
                label_visibility="collapsed",
                default=current_mode
            )
            
            # Handle selection
            if selection == "compare" and not st.session_state.show_diff:
                st.session_state.show_diff = True
                st.rerun()
            elif selection == "preview" and st.session_state.show_diff:
                st.session_state.show_diff = False
                st.rerun()
            elif selection == "rollback":
                st.session_state.rollback_target = st.session_state.viewing_version
                st.rerun()


def render_action_buttons():
    """Render action buttons for PRD operations"""
    col_actions = st.columns(3)
    
    with col_actions[0]:
        if st.button("📊 Show Changes", use_container_width=True):
            st.session_state.show_diff = not st.session_state.show_diff
            st.rerun()
    
    with col_actions[1]:
        if st.button("📥 Download", use_container_width=True):
            # This will be handled by the main app
            pass
    
    with col_actions[2]:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()


def render_prd_content_container():
    """Render the main PRD content container"""
    return st.container()


def render_prd_preview_content(current_content: str, loading: bool = False, message: str = "🤖 AI is updating your PRD..."):
    """Render PRD content box with optional loading overlay.

    Args:
        current_content: The PRD markdown/html content to display.
        loading: When True, renders a semi-transparent overlay with spinner on top of current content.
        message: Loading message to show in the overlay.
    """
    if loading:
        st.markdown(
            f"""
            <div class='prd-preview' style='position: relative;'>
                {current_content}
                <div class="loading-overlay">
                    <div class="loading-content">
                        <div class="spinner"></div>
                        <div class="loading-text">{message}</div>
                        <div class="loading-subtext">
                            Analyzing your request and generating an improved version of the document.<br/>
                            This may take a few moments.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class='prd-preview'>
                {current_content}
            </div>
            """,
            unsafe_allow_html=True,
        )