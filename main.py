import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.utils import platform

# The exact package target matching your engine APK build
RSDK_PACKAGE_NAME = "com.wildcatdev.RSDKv4"

class UltimateRSDKLauncher(App):
    def build(self):
        self.icon = "launcher_icon.png"
        self.selected_directory = ""
        
        # Root layout container
        self.main_container = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Fire up the brand new Step 1 Instruction Screen layout
        self.show_instruction_screen()
        
        # Request system scoped file privileges automatically if platform target is active
        if platform == 'android':
            self.request_android_permissions()
            
        return self.main_container

    def show_instruction_screen(self):
        self.main_container.clear_widgets()
        
        # 1. Main Instructions Label
        instructions_text = (
            "The RSDK files for each game should be named accordingly:\n"
            "• \"S1.rsdk\" for Sonic 1\n"
            "• \"S2.rsdk\" for Sonic 2\n\n"
            "After you've done that you have to select the directory where those files are located."
        )
        
        instructions_label = Label(
            text=instructions_text,
            font_size='16sp',
            halign='center',
            valign='middle',
            size_hint=(1, 0.7)
        )
        instructions_label.bind(size=instructions_label.setter('text_size'))
        self.main_container.add_widget(instructions_label)
        
        # 2. Select Directory Button
        dir_btn = Button(
            text="Select Directory",
            font_size='18sp',
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint=(1, 0.3)
        )
        dir_btn.bind(on_press=self.open_directory_picker)
        self.main_container.add_widget(dir_btn)

    def open_directory_picker(self, instance):
        # On Android, we invoke the native storage picker or default to the standard RSDKv4 path.
        # For simplicity and ease of use, we default directly to the shared /RSDKv4 environment folder.
        default_path = "/storage/emulated/0/RSDKv4"
        
        if os.path.exists(default_path):
            self.selected_directory = default_path
        else:
            # Fallback if the folder doesn't exist yet, uses root shared storage
            self.selected_directory = "/storage/emulated/0"
            
        # Transition straight into Step 2 now that a directory path is locked in!
        self.show_game_selection_screen()

    def show_game_selection_screen(self):
        self.main_container.clear_widgets()
        
        # Header update status bar showing chosen path
        self.status_label = Label(
            text=f"Directory: {self.selected_directory}\nSelect a game to swap and launch", 
            font_size='16sp', 
            halign='center',
            size_hint=(1, 0.2)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.main_container.add_widget(self.status_label)
        
        # --- Sonic 1 Row ---
        s1_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.4), spacing=10)
        if os.path.exists("Sonic1.png"):
            s1_layout.add_widget(Image(source="Sonic1.png", size_hint=(0.4, 1)))
        
        btn_s1 = Button(
            text="Play Sonic 1", 
            font_size='20sp', 
            background_color=(0, 0.34, 0.7, 1),
            size_hint=(0.6, 1)
        )
        btn_s1.bind(on_press=lambda instance: self.handle_game_swap(game_target=1))
        s1_layout.add_widget(btn_s1)
        self.main_container.add_widget(s1_layout)
        
        # --- Sonic 2 Row ---
        s2_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.4), spacing=10)
        if os.path.exists("Sonic2.png"):
            s2_layout.add_widget(Image(source="Sonic2.png", size_hint=(0.4, 1)))
            
        btn_s2 = Button(
            text="Play Sonic 2", 
            font_size='20sp', 
            background_color=(0.9, 0.49, 0.13, 1),
            size_hint=(0.6, 1)
        )
        btn_s2.bind(on_press=lambda instance: self.handle_game_swap(game_target=2))
        s2_layout.add_widget(btn_s2)
        self.main_container.add_widget(s2_layout)

    def handle_game_swap(self, game_target):
        current_data = os.path.join(self.selected_directory, "data.rsdk")
        s1_backup = os.path.join(self.selected_directory, "S1.rsdk")
        s2_backup = os.path.join(self.selected_directory, "S2.rsdk")
        
        if not os.path.exists(self.selected_directory):
            self.status_label.text = "Error: Chosen directory no longer exists!"
            return

        try:
            if game_target == 1:
                if os.path.exists(s1_backup):
                    if os.path.exists(current_data):
                        os.rename(current_data, s2_backup)
                    os.rename(s1_backup, current_data)
                self.status_label.text = "Sonic 1 Asset Active! Launching engine..."
                
            elif game_target == 2:
                if os.path.exists(s2_backup):
                    if os.path.exists(current_data):
                        os.rename(current_data, s1_backup)
                    os.rename(s2_backup, current_data)
                self.status_label.text = "Sonic 2 Asset Active! Launching engine..."

            # Execute context switch out to launch the actual decomp application 
            self.launch_rsdk_app()

        except Exception as e:
            self.status_label.text = f"Renaming failed: {e}"

    def launch_rsdk_app(self):
        if platform == 'android':
            from jnius import autoclass
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                pm = activity.getPackageManager()
                
                launch_intent = pm.getLaunchIntentForPackage(RSDK_PACKAGE_NAME)
                if launch_intent:
                    activity.startActivity(launch_intent)
                else:
                    self.status_label.text = "Swapped! com.wildcatdev.RSDKv4 target app not found."
            except Exception as e:
                self.status_label.text = f"Launch intent exception: {e}"

    def request_android_permissions(self):
        from jnius import autoclass
        try:
            Environment = autoclass('android.os.Environment')
            if not Environment.isExternalStorageManager():
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                
                activity = PythonActivity.mActivity
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                uri = Uri.fromParts("package", activity.getPackageName(), None)
                intent.setData(uri)
                activity.startActivity(intent)
        except Exception as e:
            pass # Silent fail layout mitigation

if __name__ == '__main__':
    UltimateRSDKLauncher().run()
