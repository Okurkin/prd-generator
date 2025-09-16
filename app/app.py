import streamlit as st
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
import time

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import custom modules
from utils.file_utils import extract_text_from_file
from utils.llm_utils import generate_initial_prd, generate_interactive_prd_update, generate_change_summary
from utils.database import PRDDatabase
from utils.diff_utils import generate_side_by_side_diff, get_change_stats
from components.layout import (
    setup_page_config, load_custom_css, render_sidebar_sessions, 
    render_sidebar_download, render_sidebar_version_history, render_rollback_modal,
    render_main_layout, render_initial_setup_form, render_chat_interface,
    render_chat_input, render_historical_version_view, render_prd_preview_section,
    render_version_navigation, render_prd_content_container, render_quick_actions
)

# Initialize database
@st.cache_resource
def init_database():
    return PRDDatabase()

db = init_database()

# Page configuration
setup_page_config()

# Load custom CSS
load_custom_css()

# Handle toast notifications
if 'show_toast' in st.session_state:
    if st.session_state.show_toast == "initial_prd":
        st.toast("Initial PRD generated successfully!", icon="🚀")
    elif st.session_state.show_toast == "prd_updated":
        st.toast("PRD updated successfully!", icon="🎉")
    elif st.session_state.show_toast == "prd_error":
        st.toast("Error updating PRD!", icon="🚨")
    elif st.session_state.show_toast == "rollback_success":
        st.toast("Rollback completed successfully!", icon="✅")
    
    # Clear the toast flag
    del st.session_state.show_toast

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_prd' not in st.session_state:
    st.session_state.current_prd = ""
if 'product_name' not in st.session_state:
    st.session_state.product_name = ""
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'current_version' not in st.session_state:
    st.session_state.current_version = 1
if 'viewing_version' not in st.session_state:
    st.session_state.viewing_version = 1
if 'show_diff' not in st.session_state:
    st.session_state.show_diff = True
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

# Clean up any lingering rollback target from previous sessions/refreshes
if hasattr(st.session_state, 'rollback_target') and 'rollback_target' in st.session_state:
    if st.session_state.rollback_target is None or st.session_state.rollback_target <= 0:
        del st.session_state.rollback_target

def create_new_session():
    """Create a new chat session"""
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.current_prd = ""
    st.session_state.product_name = ""
    st.session_state.initialized = False
    st.session_state.current_version = 1
    st.session_state.viewing_version = 1
    st.session_state.show_diff = True
    
    # Mark that session was just created to trigger auto-scroll
    st.session_state.session_just_loaded = True

def load_session(session_id: str, product_name: str):
    """Load an existing session"""
    st.session_state.session_id = session_id
    st.session_state.product_name = product_name
    st.session_state.initialized = True
    st.session_state.messages = db.get_chat_history(session_id)
    
    # Load latest version
    latest_version = db.get_latest_version(session_id)
    if latest_version:
        st.session_state.current_prd = latest_version['content']
        st.session_state.current_version = latest_version['version_number']
        st.session_state.viewing_version = latest_version['version_number']
    
    st.session_state.show_diff = False
    
    # Mark that session was just loaded to trigger auto-scroll
    st.session_state.session_just_loaded = True

def download_prd():
    """Generate download for current PRD"""
    if st.session_state.current_prd:
        filename = f"PRD_{st.session_state.product_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        return st.session_state.current_prd, filename
    return None, None

def navigate_version(direction: str):
    """Navigate between versions"""
    if direction == "prev" and st.session_state.viewing_version > 1:
        st.session_state.viewing_version -= 1
        st.session_state.show_diff = True
    elif direction == "next":
        max_version = db.get_max_version_number(st.session_state.session_id)
        if st.session_state.viewing_version < max_version:
            st.session_state.viewing_version += 1
            st.session_state.show_diff = True
    elif direction == "current":
        st.session_state.viewing_version = st.session_state.current_version
        st.session_state.show_diff = False

def get_version_content(version_number: int) -> str:
    """Get content for specific version"""
    if version_number == st.session_state.current_version:
        return st.session_state.current_prd
    else:
        version_data = db.get_version_by_number(st.session_state.session_id, version_number)
        return version_data['content'] if version_data else ""

def render_chat_panel(db):
    """Render the chat panel - can be used anywhere on the page"""
    # Simple sticky wrapper
    st.markdown('<div class="fixed-col">', unsafe_allow_html=True)
    
    st.header("💬 Interactive PRD Chat")
    
    # ========== ZPRACOVÁNÍ LOADING STAVŮ NA ZAČÁTKU ==========
    # Zpracování počátečního PRD generování
    if st.session_state.is_loading and not st.session_state.initialized:
        # Extract MRD content if provided from session state
        mrd_content = st.session_state.get('temp_mrd_content', "")
        additional_context = st.session_state.get('temp_additional_context', "")
        
        # Generate initial PRD
        with st.spinner("🤖 AI is generating initial PRD..."):
            initial_prd = generate_initial_prd(mrd_content, st.session_state.product_name, additional_context)
            st.session_state.current_prd = initial_prd
            st.session_state.initialized = True
            st.session_state.current_version = 1
            st.session_state.viewing_version = 1
            
            # Save to database
            initial_prompt = f"Product: {st.session_state.product_name}"
            if mrd_content:
                initial_prompt += f"\nMRD Content: {mrd_content[:200]}..."
            if additional_context:
                initial_prompt += f"\nAdditional Context: {additional_context}"
            
            db.save_version(
                st.session_state.session_id,
                initial_prd,
                "Initial PRD",
                "Generated initial PRD from MRD and context",
                initial_prompt
            )
            
            # Add to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"I've generated an initial PRD for '{st.session_state.product_name}'. You can see it in the preview panel. How would you like to modify it?"
            })
            
            db.save_chat_message(st.session_state.session_id, "assistant", st.session_state.messages[-1]["content"])
            
            # Vyčistíme dočasné hodnoty
            if 'temp_mrd_content' in st.session_state:
                del st.session_state.temp_mrd_content
            if 'temp_additional_context' in st.session_state:
                del st.session_state.temp_additional_context
            
            # Set toast to show after rerun
            st.session_state.show_toast = "initial_prd"
        
        st.session_state.is_loading = False
        st.rerun()
    
    # Zpracování update PRD z chat zpráv
    if st.session_state.is_loading and st.session_state.initialized and st.session_state.messages:
        last_message = st.session_state.messages[-1]
        last_role = last_message.get("role") or last_message.get("type", "assistant")
        
        if last_role == "user":
            user_request = last_message.get("content", "")
            
            # Generate updated PRD
            old_prd = st.session_state.current_prd
            
            with st.spinner("🤖 AI is generating updated PRD..."):
                updated_prd = generate_interactive_prd_update(
                    st.session_state.current_prd,
                    user_request,
                    st.session_state.product_name
                )
            
            if updated_prd and not updated_prd.startswith("Error"):
                st.session_state.current_prd = updated_prd
                st.session_state.current_version += 1
                st.session_state.viewing_version = st.session_state.current_version
                
                # Generate change summary
                change_summary = generate_change_summary(old_prd, updated_prd)
                
                # Save new version
                db.save_version(
                    st.session_state.session_id,
                    updated_prd,
                    "User Request Update",
                    change_summary,
                    user_request
                )
                
                # Add assistant response
                assistant_message = f"I've updated the PRD based on your request. Changes: {change_summary}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                db.save_chat_message(st.session_state.session_id, "assistant", assistant_message)
                
                # Set toast to show after rerun
                st.session_state.show_toast = "prd_updated"
            else:
                assistant_message = f"Sorry, I encountered an error: {updated_prd}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                db.save_chat_message(st.session_state.session_id, "assistant", assistant_message)
                st.session_state.show_toast = "prd_error"
            
            st.session_state.is_loading = False
            st.rerun()
    
    # ========== NORMÁLNÍ UI LOGIKA ==========
    
    # Initial setup if not initialized
    if not st.session_state.initialized:
        product_name, mrd_file, additional_context = render_initial_setup_form()
        
        if st.button("🎯 Generate Initial PRD", use_container_width=True):
            if product_name:
                # Uložíme všechna data z formuláře do session state
                st.session_state.product_name = product_name
                st.session_state.temp_mrd_content = ""
                st.session_state.temp_additional_context = additional_context or ""
                
                # Extract MRD content if provided
                if mrd_file:
                    st.session_state.temp_mrd_content = extract_text_from_file(mrd_file)
                
                st.session_state.is_loading = True
                
                # Create session in database
                db.create_session(st.session_state.session_id, product_name)
                
                # Ihned rerun, aby se zobrazil skeleton loading
                st.rerun()
            else:
                st.error("Please enter a product name")
    
    else:
        # Chat interface
        st.write(f"**Product:** {st.session_state.product_name}")
        
        # Check if viewing current version or historical version
        if st.session_state.viewing_version == st.session_state.current_version:
            # CURRENT VERSION - Show normal chat interface
            
            # Display chat messages
            should_auto_scroll = True
            if hasattr(st.session_state, 'session_just_loaded') and st.session_state.session_just_loaded:
                # Force scroll when session is just loaded
                st.session_state.session_just_loaded = False
                should_auto_scroll = True
            render_chat_interface(st.session_state.messages, auto_scroll=should_auto_scroll)
            
            # Quick Actions before chat input
            if not st.session_state.is_loading:
                selected_action = render_quick_actions()
                
                # Handle quick action selection
                if selected_action:
                    action_prompts = {
                        "add_section": "Add a new section to the PRD with relevant details",
                        "enhance_detail": "Enhance the existing sections with more detailed information",
                        "simplify": "Simplify the PRD by making it more concise and easier to understand", 
                        "overview": "Provide a high-level overview and summary of the entire PRD",
                        "auto_improve": "Automatically improve the entire PRD by enhancing clarity, structure, completeness, and overall quality. Review all sections for consistency, accuracy, and professional presentation."
                    }
                    
                    if selected_action in action_prompts:
                        user_input = action_prompts[selected_action]
                        st.session_state.messages.append({"role": "user", "content": user_input})
                        db.save_chat_message(st.session_state.session_id, "user", user_input)
                        # Increment counter to create new input widget
                        st.session_state.input_counter = st.session_state.get('input_counter', 0) + 1
                        st.session_state.is_loading = True
                        st.rerun()
            
            # Chat input for current version
            user_input, col_send, col_clear = render_chat_input()
            
            # Update session state with current input value
            if user_input != st.session_state.get('chat_input_value', ''):
                st.session_state.chat_input_value = user_input
            
            with col_send:
                if st.button("💬 Send Message", key="send_message_btn", use_container_width=True) and user_input and not st.session_state.is_loading:
                    # Add user message
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    db.save_chat_message(st.session_state.session_id, "user", user_input)
                    
                    # Clear the input value
                    st.session_state.chat_input_value = ""
                    st.session_state.is_loading = True
                    st.rerun()
            
            with col_clear:
                if st.button("🗑️ Clear", key="clear_messages_btn", use_container_width=True):
                    st.session_state.messages = []
                    # Clear the input value
                    st.session_state.chat_input_value = ""
                    st.rerun()
        
        else:
            # HISTORICAL VERSION - Show historical view
            render_historical_version_view()
            
            # Get chat history for this historical version
            chat_data = db.get_chat_history_until_version(
                st.session_state.session_id, 
                st.session_state.viewing_version, 
                context_limit=10  # Show more context in main chat view
            )
            
            context_messages = chat_data.get('context_messages', [])
            version_message = chat_data.get('version_message')
            assistant_response = chat_data.get('assistant_response')
            
            # Display context messages (previous conversation)
            if context_messages:
                st.write("**Previous conversation:**")
                for message in context_messages:
                    role = message.get("role", "assistant")
                    content = message.get("content", "")
                    
                    if role == "user":
                        st.markdown(f"""
                        <div style="
                            background-color: #f8f9fa;
                            border-left: 3px solid #6c757d;
                            padding: 8px 12px;
                            margin: 4px 0;
                            border-radius: 4px;
                            font-size: 13px;
                            opacity: 0.8;
                        ">
                            <strong>👤 You:</strong> {content}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="
                            background-color: #f8f9fa;
                            border-left: 3px solid #6c757d;
                            padding: 8px 12px;
                            margin: 4px 0;
                            border-radius: 4px;
                            font-size: 13px;
                            opacity: 0.8;
                        ">
                            <strong>🤖 Assistant:</strong> {content}
                        </div>
                        """, unsafe_allow_html=True)
            
            # Display the version message (the request that created this version)
            if version_message:
                st.write("**💥 Request that created this version:**")
                role = version_message.get("role", "user")
                content = version_message.get("content", "")
                
                if role == "user":
                    st.markdown(f"""
                    <div style="
                        background-color: #e3f2fd;
                        border: 2px solid #2196f3;
                        padding: 12px 16px;
                        margin: 8px 0;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                        box-shadow: 0 2px 6px rgba(33, 150, 243, 0.2);
                    ">
                        <strong>👤 You:</strong> {content}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display the assistant response for this version
            if assistant_response:
                st.write("**🤖 Agent response:**")
                content = assistant_response.get("content", "")
                st.markdown(f"""
                <div style="
                    background-color: #e8f5e8;
                    border: 2px solid #4caf50;
                    padding: 12px 16px;
                    margin: 8px 0;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    box-shadow: 0 2px 6px rgba(76, 175, 80, 0.2);
                ">
                    <strong>🤖 Assistant:</strong> {content}
                </div>
                """, unsafe_allow_html=True)
            
            # Message about returning to current version to continue chatting
            st.markdown("---")
            st.info("💡 To continue the conversation, return to the latest version using the sidebar.")
    
    # Close sticky wrapper
    st.markdown('</div>', unsafe_allow_html=True)


def render_prd_panel(db):
    """Render the PRD preview panel with loading overlay and version navigation"""
    render_prd_preview_section()

    # Pokud ještě není inicializováno
    if not st.session_state.initialized:
        # Pokud generujeme počáteční PRD, zobrazíme skeleton
        if st.session_state.is_loading:
            from components.layout import render_prd_skeleton_loading
            render_prd_skeleton_loading("🤖 AI is generating your initial PRD...")
        else:
            st.info("👈 Start by creating an initial PRD in the chat panel")
        return

    # Navigace mezi verzemi
    versions = db.get_versions(st.session_state.session_id)
    if versions:
        render_version_navigation(versions)

    # Obsah pro aktuálně vybranou verzi
    current_content = get_version_content(st.session_state.viewing_version)

    # Kontejner pro preview
    preview_container = render_prd_content_container()
    with preview_container:
        # === LOADING STAV S SKELETON ===
        if (
            st.session_state.is_loading
            and st.session_state.viewing_version == st.session_state.current_version
        ):
            from components.layout import render_prd_skeleton_loading
            # Použijeme skeleton loading místo obyčejného overlay
            render_prd_skeleton_loading("🤖 AI is updating your PRD...")
            return

        # === DIFF VIEW ===
        if st.session_state.show_diff and st.session_state.viewing_version > 1:
            previous_content = get_version_content(
                st.session_state.viewing_version - 1
            )
            if previous_content:
                stats = get_change_stats(previous_content, current_content)
                st.markdown(
                    f"**Changes:** +{stats['lines_added']} / -{stats['lines_removed']} "
                    f"(Similarity: {stats['similarity_ratio']:.1%})"
                )
                diff_html = generate_side_by_side_diff(
                    previous_content, current_content
                )
                st.markdown(
                    f'<div class="diff-view">{diff_html}</div>', unsafe_allow_html=True
                )
        else:
            # === NORMÁLNÍ VIEW ===
            from components.layout import render_prd_preview_content
            render_prd_preview_content(current_content, loading=False)



# Sidebar for session management and history
# Sidebar for session management and history
with st.sidebar:
    # Load all sessions
    all_sessions = db.get_all_sessions()
    
    render_sidebar_sessions(db, all_sessions, create_new_session, load_session)
    
    st.divider()
    
    # Download PRD section
    render_sidebar_download(download_prd)
    
    # Version History
    if st.session_state.initialized:
        versions = db.get_versions(st.session_state.session_id)
        if versions:
            render_sidebar_version_history(db, versions)

# Global cleanup for rollback modal - clear if user navigated away
if hasattr(st.session_state, 'rollback_target') and st.session_state.rollback_target is not None:
    # Track the last version user was viewing
    if 'last_viewing_version' not in st.session_state:
        st.session_state.last_viewing_version = st.session_state.viewing_version
    
    # If user changed version or navigated away, clear rollback target
    if st.session_state.viewing_version != st.session_state.last_viewing_version:
        st.session_state.rollback_target = None
    
    st.session_state.last_viewing_version = st.session_state.viewing_version

# Rollback confirmation modal
render_rollback_modal(db)

# Main content area
col1, col2 = render_main_layout()

with col1:
    render_prd_panel(db)

with col2:
    render_chat_panel(db)

# Footer
st.markdown("---")
st.markdown("**AI PRD Generator v2.0** - Interactive chat with version control and diff viewing")
