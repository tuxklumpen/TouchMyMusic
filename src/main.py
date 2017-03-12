from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.popup import Popup
from spotifycover import get_images
from mpd import MPDClient
from os import path
import urllib
import threading

FILE = 'file'
ARTIST = 'artist'
ALBUM = 'album'
TITLE = 'title'

class Album(RecycleDataViewBehavior, ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(Album, self).__init__(**kwargs)
        
    def refresh_view_attrs(self, rv, index, data):
        self.ids['title'].text = data['title']
        if 'cover' in data['data'].keys():
            print(data['data']['cover'])
            self.ids['cover'].source = data['data']['cover']
        else:
            self.ids['cover'].source = 'https://upload.wikimedia.org/wikipedia/en/f/fa/Keith_Jarrett_Koln_Concert_Cover.jpg'
        return super(Album, self).refresh_view_attrs(
            rv, index, data)
        
    def on_press(self):
        player.play_tracks(self.data['tracks'])

class ArtworkSlider(RecycleView):
    def __init__(self, **kwargs):
        super(ArtworkSlider, self).__init__(**kwargs)
        
    def update(self, albums):
        self.data = []
        for album, data in albums.items():
            self.data.append({'title' : album, 'data' : data})
            
        print(self.data)

class Player():
    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)       
        self.mpd_client = MPDClient()
        
    def connect(self):        
        self.mpd_client.connect('192.168.55.138', 6600)
        pass
        
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
        res = self.mpd_client.search("any", string)  
        return res
    
    def play_tracks(self, tracks):
        self.mpd_client.clear()
        for track in tracks:
            self.mpd_client.add(track['file'])
        self.mpd_client.play()
        
    def list(self):
        playlist = ["{0} - {1} - {2}".format(song['title'], song['album'], song['artist']) for song in self.mpd_client.playlistinfo()]
        print(playlist)
        return playlist

class RadioButton(Button):
    def on_press(self):
        print('play ', self.text, ' link ', self.link)
        player.play_station(self.link)

class LibraryScreen(BoxLayout):
    def __init__(self, interface, **kwargs):
        super(LibraryScreen, self).__init__(**kwargs)
        
    def search(self):
        search_string = self.ids['searchinput'].text
        res = player.search(search_string)
        
        print(res)
        
        local_res = {}
        spotify_res = {}
        for r in res:
            if 'local' in r[FILE]:
                if 'track' in r[FILE]:
                    if r[ALBUM] not in local_res.keys():
                        local_res[r[ALBUM]] = {'tracks' : []}
                    local_res[r[ALBUM]]['tracks'].append(r)
         
        for r in res:
            if 'spotify' in r[FILE]:
                if 'track' in r[FILE]:
                    if  r[ALBUM] not in local_res.keys():
                        if r[ALBUM] not in spotify_res.keys():
                            spotify_res[r[ALBUM]] = {'tracks' : [], 'uri' : r['x-albumuri']}
                        spotify_res[r[ALBUM]]['tracks'].append(r)
                        
        cover_art = get_images([spotify_res[album]['uri'] for album in spotify_res.keys()])
        for album in spotify_res.keys():            
            url = spotify_res[album]['uri']
            spotify_res[album]['cover'] = cover_art[url][0]['url']
    
        albums = local_res
        albums.update(spotify_res)
        
        self.ids['result'].update(albums)

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
        
class PlayList(RecycleView):
    def __init__(self, data, **kwargs):
        super(PlayList, self).__init__(**kwargs)
        self.data = data
                
class StatusLabel(Button):
    def update(self, info):
        if 'title' in info.keys():
            self.text = info['title']
            
    def on_press(self):
        playlist = player.list()
        popup = Popup(title='Current Playlist',
                content=PlayList(data = [{'text': item} for item in playlist]))
        popup.open()
    
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

