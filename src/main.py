from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.button import Button
from mpd import MPDClient

mpd_client = None

def play_station(link):
    mpd_client.clear()
    mpd_client.add(link)
    mpd_client.play()
    
class PlayButton(Button):
    

class RadioButton(Button):
    def on_press(self):
        print('play ', self.text, ' link ', self.link)
        play_station(self.link)


class LibraryScreen(BoxLayout):
    def __init__(self, interface, **kwargs):
        super(LibraryScreen, self).__init__(**kwargs)

class RadioScreen(RecycleView):
    def __init__(self, interface, **kwargs):
        super(RadioScreen, self).__init__(**kwargs)
        self.data = [{'text' : 'SWR2', 'link' : 'http://mp3-live.swr.de/swr2_m.m3u'},
                     {'text' : 'KJazz', 'link' : 'http://stream.kjzz.org/kjzz_mp3_128.pls'}]
                    
class SpotifyScreen(BoxLayout):
    def __init__(self, interface, **kwargs):
        super(SpotifyScreen, self).__init__(**kwargs)

class HomeScreen(GridLayout):
    def __init__(self, interface, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.interface = interface
        
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
    
class StatusBar(BoxLayout):
    pass
    
class OverlayInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(OverlayInterface, self).__init__(**kwargs)
        
        self.add_widget(Interface())
        
        status_bar = StatusBar(size_hint=(1,.1))
        self.add_widget(status_bar)
    
class TmmApp(App):
    def build(self):
        return OverlayInterface()

if __name__ == '__main__':
    mpd_client = MPDClient()
    mpd_client.connect('192.168.55.138', 6600)
    
    TmmApp().run()
    
    mpd_client.close()
    mpd_client.disconnect()
