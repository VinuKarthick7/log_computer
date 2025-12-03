"""
Lab Session Auto-Logout on System Shutdown
Detects shutdown and logs out active sessions with GUI popup
Updated with matching color theme
"""

import requests
import os
import sys
import tkinter as tk
from datetime import datetime
import threading

# Configuration
SERVER_URL = "http://localhost:5000"
SESSION_FILE = "current_session.txt"

# Color Theme - Matching Registration Page
COLORS = {
    'primary_bg': '#1A1F2E',
    'secondary_bg': '#252B3B',
    'card_bg': '#2A3142',
    'accent_blue': '#0EA5E9',
    'text_primary': '#F8FAFC',
    'text_secondary': '#94A3B8',
    'text_muted': '#64748B',
    'border': '#3A4353',
    'success': '#10B981',
    'warning': '#F59E0B'
}

def load_session():
    """Load active session from file."""
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    parts = content.split('|')
                    if len(parts) >= 3:
                        return {
                            'session_id': parts[0],
                            'register_no': parts[1],
                            'name': parts[2]
                        }
    except Exception as e:
        print(f"Error loading session: {e}")
    return None

def logout_session(session_info):
    """Send logout request to server."""
    try:
        print(f"Logging out: {session_info['name']}")
        
        response = requests.post(
            f"{SERVER_URL}/api/logout",
            json={"session_id": session_info['session_id']},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("Logout successful!")
                # Remove session file
                if os.path.exists(SESSION_FILE):
                    os.remove(SESSION_FILE)
                return True
            else:
                print(f"Logout failed: {data.get('error')}")
        else:
            print(f"Server error: {response.status_code}")
            
    except Exception as e:
        print(f"Network error: {e}")
    
    return False

def show_popup(session_info):
    """Show GUI popup during logout with matching theme."""
    root = tk.Tk()
    root.title("Lab Session - System Shutdown")
    root.geometry("480x320")
    root.configure(bg=COLORS['primary_bg'])
    root.resizable(False, False)
    root.attributes('-topmost', True)
    root.overrideredirect(True)  # Remove window border
    
    # Center window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - 240
    y = (screen_height // 2) - 160
    root.geometry(f'480x320+{x}+{y}')
    
    # Main container with border
    container = tk.Frame(root, bg=COLORS['secondary_bg'], bd=1, highlightthickness=1, 
                        highlightbackground=COLORS['border'])
    container.pack(fill='both', expand=True, padx=0, pady=0)
    
    # Header section
    header_frame = tk.Frame(container, bg=COLORS['primary_bg'])
    header_frame.pack(fill='x', pady=0)
    
    # Icon
    icon_label = tk.Label(
        header_frame,
        text="🚪",
        font=('Segoe UI Emoji', 50),
        bg=COLORS['primary_bg'],
        fg=COLORS['text_primary']
    )
    icon_label.pack(pady=(25, 10))
    
    # Title
    title_label = tk.Label(
        header_frame,
        text="System Shutdown Detected",
        font=('Segoe UI', 16, 'bold'),
        bg=COLORS['primary_bg'],
        fg=COLORS['text_primary']
    )
    title_label.pack(pady=(0, 5))
    
    # Subtitle
    subtitle_label = tk.Label(
        header_frame,
        text="Logging out from lab session",
        font=('Segoe UI', 10),
        bg=COLORS['primary_bg'],
        fg=COLORS['text_secondary']
    )
    subtitle_label.pack(pady=(0, 20))
    
    # Session info card
    info_card = tk.Frame(container, bg=COLORS['card_bg'], bd=1, 
                         highlightthickness=1, highlightbackground=COLORS['border'])
    info_card.pack(padx=30, pady=(0, 20), fill='x')
    
    # Info header
    info_header = tk.Label(
        info_card,
        text="Active Session",
        font=('Segoe UI', 9, 'bold'),
        bg=COLORS['card_bg'],
        fg=COLORS['text_muted'],
        anchor='w',
        padx=15,
        pady=8
    )
    info_header.pack(fill='x')
    
    # Divider
    divider = tk.Frame(info_card, bg=COLORS['border'], height=1)
    divider.pack(fill='x')
    
    # Name row
    name_frame = tk.Frame(info_card, bg=COLORS['card_bg'])
    name_frame.pack(fill='x', padx=15, pady=8)
    
    name_icon = tk.Label(
        name_frame,
        text="👤",
        font=('Segoe UI Emoji', 14),
        bg=COLORS['card_bg'],
        fg=COLORS['text_primary']
    )
    name_icon.pack(side='left', padx=(0, 10))
    
    name_label = tk.Label(
        name_frame,
        text=session_info['name'],
        font=('Segoe UI', 12, 'bold'),
        bg=COLORS['card_bg'],
        fg=COLORS['text_primary'],
        anchor='w'
    )
    name_label.pack(side='left', fill='x')
    
    # Register number row
    reg_frame = tk.Frame(info_card, bg=COLORS['card_bg'])
    reg_frame.pack(fill='x', padx=15, pady=(0, 10))
    
    reg_icon = tk.Label(
        reg_frame,
        text="🎓",
        font=('Segoe UI Emoji', 12),
        bg=COLORS['card_bg'],
        fg=COLORS['text_secondary']
    )
    reg_icon.pack(side='left', padx=(0, 10))
    
    reg_label = tk.Label(
        reg_frame,
        text=session_info['register_no'],
        font=('Segoe UI', 10),
        bg=COLORS['card_bg'],
        fg=COLORS['text_secondary'],
        anchor='w'
    )
    reg_label.pack(side='left', fill='x')
    
    # Status section
    status_frame = tk.Frame(container, bg=COLORS['primary_bg'])
    status_frame.pack(fill='x', pady=(0, 15))
    
    # Status message
    status_label = tk.Label(
        status_frame,
        text="Processing logout...",
        font=('Segoe UI', 11),
        bg=COLORS['primary_bg'],
        fg=COLORS['accent_blue']
    )
    status_label.pack(pady=(10, 5))
    
    # Progress indicator
    progress_label = tk.Label(
        status_frame,
        text="●",
        font=('Segoe UI', 14),
        bg=COLORS['primary_bg'],
        fg=COLORS['accent_blue']
    )
    progress_label.pack(pady=(0, 10))
    
    # Variables for animation
    countdown = [3]
    logout_done = [False]
    logout_success = [False]
    
    def animate_progress():
        """Animate progress dots."""
        if countdown[0] > 0:
            dots = "●" * (4 - countdown[0])
            progress_label.config(text=dots)
            countdown[0] -= 1
            root.after(700, animate_progress)
        else:
            # Close after animation
            root.after(500, root.destroy)
    
    def perform_logout():
        """Perform logout in background thread."""
        success = logout_session(session_info)
        logout_done[0] = True
        logout_success[0] = success
        
        # Update status on main thread
        def update_status():
            if success:
                status_label.config(
                    text="✓ Logout successful!",
                    fg=COLORS['success']
                )
                progress_label.config(fg=COLORS['success'])
            else:
                status_label.config(
                    text="⚠ Logout failed - please check manually",
                    fg=COLORS['warning']
                )
                progress_label.config(fg=COLORS['warning'])
        
        root.after(0, update_status)
    
    # Start logout in background thread
    logout_thread = threading.Thread(target=perform_logout, daemon=True)
    logout_thread.start()
    
    # Start progress animation
    animate_progress()
    
    # Run GUI
    root.mainloop()
    
    return logout_success[0]

def main():
    """Main entry point."""
    # Log to file
    log_file = "shutdown_log.txt"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Shutdown Handler Triggered\n")
        f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n")
    
    print("\n" + "="*60)
    print("Lab Session Shutdown Handler")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Load active session
    session_info = load_session()
    
    if session_info:
        print(f"\n✓ Active session found")
        print(f"  Name: {session_info['name']}")
        print(f"  Register No: {session_info['register_no']}")
        print("\nShowing logout popup...")
        
        # Show popup and logout
        success = show_popup(session_info)
        
        result = "SUCCESS" if success else "FAILED"
        print(f"\nLogout Result: {result}")
        
        # Log result
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Session: {session_info['name']} ({session_info['register_no']})\n")
            f.write(f"Result: {result}\n")
    else:
        print("\n✓ No active session found")
        print("Nothing to logout")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("No active session\n")
    
    print("\nHandler completed")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        with open("shutdown_log.txt", 'a') as f:
            f.write(f"ERROR: {e}\n")
