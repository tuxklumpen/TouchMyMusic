from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty
from mpd import MPDClient
import threading

class Player():
    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)       
        self.mpd_client = MPDClient()
        
    def connect(self):        
        self.mpd_client.connect('192.168.55.138', 6600)
        
    def disconnect(self):
        self.mpd_client.clear()    
        self.mpd_client.close()
        self.mpd_client.disconnect()
        
    def play_station(self, link):
        self.mpd_client.clear()
        self.mpd_client.add(link)
        self.mpd_client.play()
        
    def play_pause(self):
        self.mpd_client.pause()
        
    def search(self, string):
        res = self.mpd_client.find("any", string)  

class RadioButton(Button):
    def on_press(self):
        print('play ', self.text, ' link ', self.link)
        player.play_station(self.link)

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
        
def check_updates(status_bar):
    client = MPDClient()
    client.connect('192.168.55.138', 6600)
    while True:
        print('idle')
        client.idle()
        print('update')
        status_bar.set_text(client.currentsong())

class PlayButton(Button):
    def on_press(self):
        print("Play/Pause")
        player.play_pause()
        
class StatusLabel(Label):
    def update(self, info):
        if 'title' in info.keys():
            self.text = info['title']
    
class StatusBar(BoxLayout):
    def __init__(self, interface, **kwargs):
        super(StatusBar, self).__init__(**kwargs)
        
        self.interface = interface
        
        self.cu = threading.Thread(None, check_updates, "CheckUpdates", [self])
        self.cu.start()
        
    def info_panel(self):
        return self.ids['status']
    
    def set_text(self, song):
        self.ids['status'].update(song)
            
class OverlayInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(OverlayInterface, self).__init__(**kwargs)
        
        interface = Interface()
        self.add_widget(interface)
        
        status_bar = StatusBar(interface, size_hint=(1,.1))
        self.add_widget(status_bar)
    
class TmmApp(App):
    def build(self):
        return OverlayInterface()

if __name__ == '__main__':
    player = Player()
    player.connect()    
    TmmApp().run()
    player.disconnect()

