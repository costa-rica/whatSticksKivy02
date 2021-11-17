from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivymd.uix.toolbar import MDToolbar
from kivy.graphics import Rectangle, Color
from kivymd.uix.textfield import MDTextField
from kivy.core.window import Window
import requests
from kivy.properties import ObjectProperty, ColorProperty
from kivymd.uix.toolbar import MDToolbar
from kivy.core.window import Window
from kivy.utils import platform
import datetime;from datetime import timedelta
from utils import add_activity_util, current_time_util
import json
from kivy.uix.widget import Widget
# import time
# import pytz

if platform in ['ios','android']:
    print('kivy.utils.platform:::', platform,)
else:
    Window.size = (640, 1136)#iphone demensions

class ParentScreen1(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        screenbackground=CanvasWidget()
        self.add_widget(screenbackground,index=99)

    def login_button(self):

        response = requests.request('GET','http://api.what-sticks-health.com/get_users',
            auth=(self.email.text,self.password.text))
        print('email/password::', self.email.text, self.password.text)
        print("response:::",response.status_code)

        # if response.status_code ==200:
        #     self.app.psm.current="ps2"
        if response.status_code ==200:
            # print(json.loads(response.content.decode('utf-8')))
            for i in json.loads(response.content.decode('utf-8')):
                if i['email']==self.email.text:

                    ActivityScreen.user_name_str=i['username']
                    ParentScreen2.user_timezone=i['user_timezone']
                    # print('i[user_timezone;;;;',i['user_timezone'])
                    ActivityScreen.user_id_str=i['id']
                    ParentScreen2.email=self.email.text
                    ActivityScreen.email=self.email.text
                    print('ParentScreen1 login_button email:::',self.email.text)

                    #sm.current = 'main'
                    self.app.psm.current="ps2"
        else:
            invalidLogin()

class CanvasWidget(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(127/255,160/255,189/255,1)
            self.rect=Rectangle(pos=self.pos,size=self.size)
            self.bind(pos=self.update_rect,
                          size=self.update_rect)
    def update_rect(self, *args):
            self.rect.pos = self.pos
            self.rect.size = self.size

class ParentScreen2(Screen):
    user_timezone=''
    email=''
    def __init__(self,**kwargs):
        super(ParentScreen2, self).__init__(**kwargs)
        self.super_box=BoxLayout(orientation ='vertical')
    #Add navigation slide out thingy
        nav_drawer=MDNavigationDrawer()
        self.nav_drawer=nav_drawer
        nav_box=NavMenu()
        nav_drawer.add_widget(nav_box)
        toolbar=Toolbar()
        toolbar.left_action_items=[["menu", lambda x: nav_drawer.set_state("open")]]
        screenbackground=CanvasWidget()
    #order of self widgets matters:
        self.add_widget(screenbackground,index=99)
        self.add_widget(self.super_box)
        self.add_widget(nav_drawer)
        self.add_widget(toolbar)

    def on_enter(self):
        ActivityScreen.user_timezone=self.user_timezone
        ActivityScreen.email=self.email
        self.csm=ChildScreenManger()
        self.super_box.add_widget(self.csm)

class ActivityScreen(Screen):
    email=''
    email_label=ObjectProperty()
    time_thing=ObjectProperty()
    date_thing=ObjectProperty()
    user_timezone=''
    # user_timezone='Europe/Paris'#'US/Eastern'
    def __init__(self,**kwargs):
        super(ActivityScreen,self).__init__(**kwargs)
        self.app=MainApp.get_running_app()
        self.date_time_obj=datetime.datetime.now()

    def on_enter(self,*args):
        print('Activity Screen on_enter email:::',self.email_label.text)
        self.email_label.text=self.email
        self.date_time_now=current_time_util(self.user_timezone)
        self.ids.date_thing.text=self.date_time_now[0]
        self.ids.time_thing.text=self.date_time_now[1]

    def log_activity(self):
        title=self.title.text
        note=self.note.text
        #combine date_thing adn time_thing into datetime object
        try:
            datetime_thing=datetime.datetime.strptime(self.ids.date_thing.text +" "+ self.ids.time_thing.text,'%m/%d/%Y %I:%M %p')
            add_activity_util(title, note,self.user_id_str,self.user_timezone,datetime_thing, self.user_email,self.user_password)
            self.add_widget(ConfirmBox())

        except ValueError:
            self.add_widget(FailBox())


class TableScreen(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        box = BoxLayout(orientation ='vertical')
        box.add_widget(MDLabel(text="Label in BoxLayout in Table Screen",
            pos_hint={'center_x':.95}))
        self.add_widget(box)

class NavMenu(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        nav_box=BoxLayout(orientation ='vertical',size_hint=(0.1,0.9))
        nav_button1 = Button(text="Button(Nav) go to childS2")
        nav_button1.bind(on_press=self.nav_change_screen1)
        nav_button2 = Button(text="Button(Nav) go to childS1")
        nav_button2.bind(on_press=self.nav_change_screen2)
        nav_box.add_widget(nav_button1)
        nav_box.add_widget(nav_button2)
        self.app=MainApp.get_running_app()


    def on_entry(self):
        print('********when does NavMenu on_entry fire?******')
        # self.csm=self.app.ps2.csm

    def nav_change_screen1(self):
        self.app.ps2.csm.current="table_screen"

    def nav_change_screen2(self):
        self.app.ps2.csm.current="activity_screen"


class Toolbar(MDToolbar):...

class ConfirmBox(BoxLayout):...

class FailBox(BoxLayout):...

class ChildScreenManger(ScreenManager):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        activity_screen=ActivityScreen(name="activity_screen")
        table_screen=TableScreen(name="table_screen")
        self.add_widget(activity_screen)
        self.add_widget(table_screen)
        self.current="activity_screen"

class MainApp(MDApp):
    def build(self):
        self.ps1=ParentScreen1(name='ps1')
        self.ps2=ParentScreen2(name='ps2')
        psm=ScreenManager()
        self.psm=psm
        psm.add_widget(self.ps1)
        psm.add_widget(self.ps2)
        self.icon = "icon.png"


        return psm


MainApp().run()
