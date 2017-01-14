from kivy.app import App
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.button import Button

class RadioButton(Button):
    def on_press(self):
        print('play ', self.text, ' link ', self.link)

class MusicScreen(BoxLayout):
    def __init__(self, interface, **kwargs):
        super(MusicScreen, self).__init__(**kwargs)

class RadioScreen(RecycleView):
    def __init__(self, interface, **kwargs):
        super(RadioScreen, self).__init__(**kwargs)
        self.data = [{'text' : 'SWR2', 'link' : 'http://mp3-live.swr.de/swr2_m.m3u'
                    }]

class HomeScreen(GridLayout):
    def __init__(self, interface, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.interface = interface
        
        def bind_buttons(*args):
            self.ids['musicbutton'].bind(on_press=self.interface.show)
            self.ids['radiobutton'].bind(on_press=self.interface.show)
        
        Clock.schedule_once(bind_buttons)
        
class Interface(BoxLayout):
    def __init__(self,**kwargs):
        super(Interface, self).__init__(**kwargs)
        self.widgets = {'home' : HomeScreen, 
                        'radio' : RadioScreen,
                        'music' : MusicScreen}
                        
        home = HomeScreen(self)
        self.add_widget(home)
        
    def show(self, widgetid):
        self.clear_widgets()
        widget = self.widgets[widgetid.value](self)
        self.add_widget(widget)
    
class TmmApp(App):
    def build(self):
        return Interface()

if __name__ == '__main__':
    TmmApp().run()
