import traceback

try:
    from ballsort.ui.app import BallSortApp
except Exception:
    BallSortApp = None
    err_msg = traceback.format_exc()

if __name__ == "__main__":
    if BallSortApp is None:
        try:
            from kivy.app import App
            from kivy.uix.label import Label
            class ErrorApp(App):
                def build(self):
                    return Label(text=err_msg, font_size='10sp', text_size=(None, None))
            ErrorApp().run()
        except:
            print("CRITICAL ERROR: Failed to even load Kivy ErrorApp!")
            print(err_msg)
    else:
        try:
            BallSortApp().run()
        except Exception as e:
            err_msg_run = traceback.format_exc()
            print("CRASH IN APP RUN:", err_msg_run)
            try:
                from kivy.app import App
                from kivy.uix.label import Label
                class ErrorApp(App):
                    def build(self):
                        return Label(text=err_msg_run, font_size='10sp', text_size=(None, None))
                ErrorApp().run()
            except:
                pass
