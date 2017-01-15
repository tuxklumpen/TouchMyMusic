from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.button import Button
from mpd import MPDClient

class RadioButton(Button):
    def on_press(self):
        print('play ', self.text, ' link ', self.link)
        client = MPDClient()
        client.connect('localhost', 6600)
        client.add(self.link)
        client.play()
        client.close()
        client.disconnect()

class LibraryScreen(BoxLayout):
    def __init__(self, interface, **kwargs):
        super(LibraryScreen, self).__init__(**kwargs)

class RadioScreen(RecycleView):
    def __init__(self, interface, **kwargs):
        super(RadioScreen, self).__init__(**kwargs)
        self.data = [{'text' : 'SWR2', 'link' : 'http://mp3-live.swr.de/swr2_m.m3u'
                    }]
                    
class SpotifyScreen(BoxLayout):
    def __init__(self, interface, **kwargs):
        super(SpotifyScreen, self).__init__(**kwargs)

class HomeScreen(GridLayout):
    def __init__(self, interface, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.interface = interface
      
        
    def show(self, widgetid):
        self.interface.show(self.widgets[widgetid](self.interface))
        
class Interface(BoxLayout):
    def __init__(self,**kwargs):
        super(Interface, self).__init__(**kwargs)
                                
        self.widgets = {'home' : HomeScreen, 
                'radio' : RadioScreen,
                'library' : LibraryScreen,
                'spotify' : SpotifyScreen}
                                
        home = HomeScreen(self)
        self.add_widget(home)
        
    def set_widgets(self, widgets):
        self.widgets = widgets
        
    def show(self, widgetid):
        print("Switch to {0}".format(widgetid.value))
        self.clear_widgets()
        self.add_widget(self.widgets[widgetid.value](self))
    
class TmmApp(App):
    def build(self):
        return Interface()

if __name__ == '__main__':
    TmmApp().run()
